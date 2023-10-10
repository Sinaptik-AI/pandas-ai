import time
from typing import Optional
from unittest.mock import Mock, patch
import pandas as pd
import pytest

from pandasai.helpers.query_exec_tracker import QueryExecTracker
from pandasai.llm.fake import FakeLLM
from pandasai.smart_dataframe import SmartDataframe
from unittest import TestCase


assert_almost_equal = TestCase().assertAlmostEqual


class TestQueryExecTracker:
    @pytest.fixture
    def llm(self, output: Optional[str] = None):
        return FakeLLM(output=output)

    @pytest.fixture
    def sample_df(self):
        return pd.DataFrame(
            {
                "country": [
                    "United States",
                    "United Kingdom",
                    "France",
                    "Germany",
                    "Italy",
                    "Spain",
                    "Canada",
                    "Australia",
                    "Japan",
                    "China",
                ],
                "gdp": [
                    19294482071552,
                    2891615567872,
                    2411255037952,
                    3435817336832,
                    1745433788416,
                    1181205135360,
                    1607402389504,
                    1490967855104,
                    4380756541440,
                    14631844184064,
                ],
                "happiness_index": [
                    6.94,
                    7.16,
                    6.66,
                    7.07,
                    6.38,
                    6.4,
                    7.23,
                    7.22,
                    5.87,
                    5.12,
                ],
            }
        )

    @pytest.fixture
    def smart_dataframe(self, llm, sample_df):
        return SmartDataframe(sample_df, config={"llm": llm, "enable_cache": False})

    @pytest.fixture
    def smart_datalake(self, smart_dataframe: SmartDataframe):
        return smart_dataframe.lake

    @pytest.fixture
    def tracker(self):
        return QueryExecTracker(
            conversation_id="123",
            query="which country has the highest GDP?",
            instance="SmartDatalake",
            output_type="json",
        )

    def test_add_dataframes(
        self, smart_dataframe: SmartDataframe, tracker: QueryExecTracker
    ):
        # Add the dataframe to the tracker
        tracker._dataframes = []
        tracker.add_dataframes([smart_dataframe])

        # Check if the dataframe was added correctly
        assert len(tracker._dataframes) == 1
        assert len(tracker._dataframes[0]["headers"]) == 3
        assert len(tracker._dataframes[0]["rows"]) == 5

    def test_add_step(self, tracker: QueryExecTracker):
        # Create a sample step
        step = {"type": "CustomStep", "description": "This is a custom step."}

        tracker._steps = []
        # Add the step to the tracker
        tracker.add_step(step)

        # Check if the step was added correctly
        assert len(tracker._steps) == 1
        assert tracker._steps[0] == step

    def test_format_response_dataframe(
        self, tracker: QueryExecTracker, sample_df: pd.DataFrame
    ):
        # Create a sample ResponseType for a dataframe
        response = {"type": "dataframe", "value": sample_df}

        # Format the response using _format_response
        formatted_response = tracker._format_response(response)

        # Check if the response is formatted correctly
        assert formatted_response["type"] == "dataframe"
        assert len(formatted_response["value"]["headers"]) == 3
        assert len(formatted_response["value"]["rows"]) == 10

    def test_format_response_other_type(self, tracker: QueryExecTracker):
        # Create a sample ResponseType for a non-dataframe response
        response = {
            "type": "other_type",
            "value": "SomeValue",
        }

        # Format the response using _format_response
        formatted_response = tracker._format_response(response)

        # Check if the response is formatted correctly
        assert formatted_response["type"] == "other_type"
        assert formatted_response["value"] == "SomeValue"

    def test_get_summary(self, tracker: QueryExecTracker):
        # Execute a mock function to generate some steps and response
        def mock_function(*args, **kwargs):
            return "Mock Result"

        tracker.execute_func(mock_function, tag="custom_tag")

        # Get the summary
        summary = tracker.get_summary()

        # Check if the summary contains the expected keys
        assert "query_info" in summary
        assert "dataframes" in summary
        assert "steps" in summary
        assert "response" in summary
        assert "execution_time" in summary

    def test_get_execution_time(self, tracker: QueryExecTracker):
        def mock_function(*args, **kwargs):
            time.sleep(1)
            return "Mock Result"

        # Sleep for a while to simulate execution time
        with patch("time.time", return_value=0):
            tracker.execute_func(mock_function, tag="cache_hit")

        # Get the execution time
        execution_time = tracker.get_execution_time()

        # Check if the execution time is approximately 1 second
        assert_almost_equal(execution_time, 1.0, delta=0.3)

    def test_execute_func_success(self, tracker: QueryExecTracker):
        tracker._steps = []

        # Create a mock function
        mock_return_value = Mock()
        mock_return_value.to_string = Mock()
        mock_return_value.to_string.return_value = "Mock Result"

        mock_func = Mock()
        mock_func.return_value = mock_return_value

        # Execute the mock function using execute_func
        result = tracker.execute_func(mock_func, tag="_get_prompt")

        # Check if the result is as expected
        assert result.to_string() == "Mock Result"
        # Check if the step was added correctly
        assert len(tracker._steps) == 1
        step = tracker._steps[0]
        assert step["type"] == "Generate Prompt"
        assert step["success"] is True

    def test_execute_func_failure(self, tracker: QueryExecTracker):
        # Create a mock function that raises an exception
        def mock_function(*args, **kwargs):
            raise Exception("Mock Exception")

        with pytest.raises(Exception):
            tracker.execute_func(mock_function, tag="custom_tag")

    def test_execute_func_cache_hit(self, tracker: QueryExecTracker):
        tracker._steps = []

        mock_func = Mock()
        mock_func.return_value = "code"

        # Execute the mock function using execute_func
        result = tracker.execute_func(mock_func, tag="cache_hit")

        # Check if the result is as expected
        assert result == "code"
        # Check if the step was added correctly
        assert len(tracker._steps) == 1
        step = tracker._steps[0]
        assert "code_generated" in step
        assert step["type"] == "Cache Hit"
        assert step["success"] is True

    def test_execute_func_generate_code(self, tracker: QueryExecTracker):
        tracker._steps = []

        # Create a mock function
        mock_func = Mock()
        mock_func.return_value = "code"

        # Execute the mock function using execute_func
        result = tracker.execute_func(mock_func, tag="generate_code")

        # Check if the result is as expected
        assert result == "code"
        # Check if the step was added correctly
        assert len(tracker._steps) == 1
        step = tracker._steps[0]
        assert "code_generated" in step
        assert step["type"] == "Generate Code"
        assert step["success"] is True

    def test_execute_func_re_rerun_code(self, tracker: QueryExecTracker):
        tracker._steps = []

        # Create a mock function
        mock_func = Mock()
        mock_func.return_value = "code"

        # Execute the mock function using execute_func
        result = tracker.execute_func(mock_func, tag="_retry_run_code")

        # Check if the result is as expected
        assert result == "code"
        # Check if the step was added correctly
        assert len(tracker._steps) == 1
        step = tracker._steps[0]
        assert "code_generated" in step
        assert step["type"] == "Retry Code Generation"
        assert step["success"] is True

    def test_execute_func_execute_code_success(
        self, sample_df: pd.DataFrame, tracker: QueryExecTracker
    ):
        tracker._steps = []

        mock_func = Mock()
        mock_func.return_value = {"type": "dataframe", "value": sample_df}

        # Execute the mock function using execute_func
        result = tracker.execute_func(mock_func, tag="execute_code")

        # Check if the result is as expected
        assert result["type"] == "dataframe"
        # Check if the step was added correctly
        assert len(tracker._steps) == 1
        step = tracker._steps[0]
        assert "result" in step
        assert step["type"] == "Code Execution"
        assert step["success"] is True

    def test_execute_func_execute_code_fail(
        self, sample_df: pd.DataFrame, tracker: QueryExecTracker
    ):
        tracker._steps = []

        def mock_function(*args, **kwargs):
            raise Exception("Mock Exception")

        with pytest.raises(Exception):
            tracker.execute_func(mock_function, tag="execute_code")

        assert len(tracker._steps) == 1
        step = tracker._steps[0]
        assert step["type"] == "Code Execution"
        assert step["success"] is False
