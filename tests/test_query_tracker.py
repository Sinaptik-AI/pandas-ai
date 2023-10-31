import os
import time
from typing import Optional
from unittest.mock import MagicMock, Mock, patch
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
        tracker = QueryExecTracker()
        tracker.start_new_track()
        tracker.add_query_info(
            conversation_id="123",
            instance="SmartDatalake",
            query="which country has the highest GDP?",
            output_type="json",
        )
        return tracker

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

    def test_get_summary(self):
        # Execute a mock function to generate some steps and response
        def mock_function(*args, **kwargs):
            return "Mock Result"

        tracker = QueryExecTracker()

        tracker.start_new_track()

        tracker.add_query_info(
            conversation_id="123",
            instance="SmartDatalake",
            query="which country has the highest GDP?",
            output_type="json",
        )

        # Get the summary
        summary = tracker.get_summary()

        tracker.execute_func(mock_function, tag="custom_tag")

        # Check if the summary contains the expected keys
        assert "query_info" in summary
        assert "dataframes" in summary
        assert "steps" in summary
        assert "response" in summary
        assert "execution_time" in summary
        assert "is_related_query" in summary["query_info"]

    def test_related_query_in_summary(self):
        # Execute a mock function to generate some steps and response
        def mock_function(*args, **kwargs):
            return "Mock Result"

        tracker = QueryExecTracker()

        tracker.set_related_query(False)

        tracker.start_new_track()

        tracker.add_query_info(
            conversation_id="123",
            instance="SmartDatalake",
            query="which country has the highest GDP?",
            output_type="json",
        )

        # Get the summary
        summary = tracker.get_summary()

        tracker.execute_func(mock_function, tag="custom_tag")

        # Check if the summary contains the expected keys
        assert "is_related_query" in summary["query_info"]
        assert not summary["query_info"]["is_related_query"]

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
        mock_func.__name__ = "_get_prompt"

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
        mock_func.__name__ = "get"

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
        mock_func.__name__ = "generate_code"

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
        mock_func.__name__ = "_retry_run_code"

        # Execute the mock function using execute_func
        result = tracker.execute_func(mock_func)

        # Execute the mock function using execute_func
        result = tracker.execute_func(mock_func)

        # Check if the result is as expected
        assert result == "code"
        # Check if the step was added correctly
        assert len(tracker._steps) == 2
        step = tracker._steps[0]
        assert "code_generated" in step
        assert step["type"] == "Retry Code Generation (1)"
        assert step["success"] is True

        # Check second step as well
        step2 = tracker._steps[1]
        assert "code_generated" in step2
        assert step2["type"] == "Retry Code Generation (2)"
        assert step2["success"] is True

    def test_execute_func_execute_code_success(
        self, sample_df: pd.DataFrame, tracker: QueryExecTracker
    ):
        tracker._steps = []

        mock_func = Mock()
        mock_func.return_value = {"type": "dataframe", "value": sample_df}
        mock_func.__name__ = "execute_code"

        # Execute the mock function using execute_func
        result = tracker.execute_func(mock_func)

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

        mock_func = Mock()
        mock_func.side_effect = Exception("Mock Exception")
        mock_func.__name__ = "execute_code"

        with pytest.raises(Exception):
            tracker.execute_func(mock_func)

        assert len(tracker._steps) == 1
        step = tracker._steps[0]
        assert step["type"] == "Code Execution"
        assert step["success"] is False

    def test_publish_method_with_server_key(self, tracker: QueryExecTracker):
        # Define a mock summary function
        def mock_get_summary():
            return "Test summary data"

        # Mock the server_config
        tracker._server_config = {
            "server_url": "http://custom-server",
            "api_key": "custom-api-key",
        }

        # Set the get_summary method to your mock
        tracker.get_summary = mock_get_summary

        # Mock the requests.post method
        mock_response = MagicMock()
        mock_response.status_code = 200
        type(mock_response).text = "Response text"
        # Mock the requests.post method
        with patch("requests.post", return_value=mock_response) as mock_post:
            # Call the publish method
            result = tracker.publish()

        # Check that requests.post was called with the expected parameters
        mock_post.assert_called_with(
            "http://custom-server/api/log/add",
            json={"json_log": "Test summary data"},
            headers={"Authorization": "Bearer custom-api-key"},
        )

        # Check the result
        assert result is None  # The function should return None

    def test_publish_method_with_no_config(self, tracker: QueryExecTracker):
        # Define a mock summary function
        def mock_get_summary():
            return "Test summary data"

        tracker._server_config = None

        # Set the get_summary method to your mock
        tracker.get_summary = mock_get_summary

        # Mock the requests.post method
        mock_response = MagicMock()
        mock_response.status_code = 200
        type(mock_response).text = "Response text"
        # Mock the requests.post method
        with patch("requests.post", return_value=mock_response) as mock_post:
            # Call the publish method
            result = tracker.publish()

        # Check that requests.post was called with the expected parameters
        mock_post.assert_not_called()

        # Check the result
        assert result is None  # The function should return None

    def test_publish_method_with_os_env(self, tracker: QueryExecTracker):
        # Define a mock summary function
        def mock_get_summary():
            return "Test summary data"

        # Define a mock environment for testing
        os.environ["LOGGING_SERVER_URL"] = "http://test-server"
        os.environ["LOGGING_SERVER_API_KEY"] = "test-api-key"

        # Set the get_summary method to your mock
        tracker.get_summary = mock_get_summary

        # Mock the requests.post method
        mock_response = MagicMock()
        mock_response.status_code = 200
        type(mock_response).text = "Response text"
        # Mock the requests.post method
        with patch("requests.post", return_value=mock_response) as mock_post:
            # Call the publish method
            result = tracker.publish()

        # Check that requests.post was called with the expected parameters
        mock_post.assert_called_with(
            "http://test-server/api/log/add",
            json={"json_log": "Test summary data"},
            headers={"Authorization": "Bearer test-api-key"},
        )

        # Check the result
        assert result is None  # The function should return None

    def test_multiple_instance_of_tracker(self, tracker: QueryExecTracker):
        # Create a mock function
        mock_func = Mock()
        mock_func.return_value = "code"
        mock_func.__name__ = "generate_code"

        # Execute the mock function using execute_func
        tracker.execute_func(mock_func, tag="generate_code")

        tracker2 = QueryExecTracker()
        tracker2.start_new_track()
        tracker2.add_query_info(
            conversation_id="12345",
            instance="SmartDatalake",
            query="which country has the highest GDP?",
            output_type="json",
        )

        assert len(tracker._steps) == 1
        assert len(tracker2._steps) == 0

        # Execute code with tracker 2
        tracker2.execute_func(mock_func, tag="generate_code")
        assert len(tracker._steps) == 1
        assert len(tracker2._steps) == 1

        # Create a mock function
        mock_func2 = Mock()
        mock_func2.return_value = "code"
        mock_func2.__name__ = "_retry_run_code"
        tracker2.execute_func(mock_func2, tag="_retry_run_code")
        assert len(tracker._steps) == 1
        assert len(tracker2._steps) == 2

        assert (
            tracker._query_info["conversation_id"]
            != tracker2._query_info["conversation_id"]
        )

    def test_conversation_id_in_different_tracks(self, tracker: QueryExecTracker):
        # Create a mock function
        mock_func = Mock()
        mock_func.return_value = "code"
        mock_func.__name__ = "generate_code"

        # Execute the mock function using execute_func
        tracker.execute_func(mock_func, tag="generate_code")

        summary = tracker.get_summary()

        tracker.start_new_track()

        tracker.add_query_info(
            conversation_id="123",
            instance="SmartDatalake",
            query="Plot the GDP's?",
            output_type="json",
        )

        # Create a mock function
        mock_func2 = Mock()
        mock_func2.return_value = "code"
        mock_func2.__name__ = "_retry_run_code"

        tracker.execute_func(mock_func2, tag="_retry_run_code")

        summary2 = tracker.get_summary()

        assert (
            summary["query_info"]["conversation_id"]
            == summary2["query_info"]["conversation_id"]
        )
        assert len(tracker._steps) == 1

    def test_reasoning_answer_in_code_section(self, tracker: QueryExecTracker):
        # Create a mock function
        mock_func = Mock()
        mock_func.return_value = ["code", "reason", "answer"]
        mock_func.__name__ = "generate_code"

        # Execute the mock function using execute_func
        tracker.execute_func(mock_func, tag="generate_code")

        summary = tracker.get_summary()

        step = summary["steps"][0]

        assert "reasoning" in step
        assert "answer" in step
        assert step["reasoning"] == "reason"
        assert step["answer"] == "answer"

    def test_reasoning_answer_in_rerun_code(self, tracker: QueryExecTracker):
        # Create a mock function
        mock_func = Mock()
        mock_func.return_value = ["code", "reason", "answer"]
        mock_func.__name__ = "_retry_run_code"

        # Execute the mock function using execute_func
        tracker.execute_func(mock_func, tag="_retry_run_code")

        summary = tracker.get_summary()

        step = summary["steps"][0]
        assert "reasoning" in step
        assert "answer" in step
        assert step["reasoning"] == "reason"
        assert step["answer"] == "answer"
