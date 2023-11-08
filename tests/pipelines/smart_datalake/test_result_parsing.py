from typing import Optional
from unittest.mock import Mock
import pandas as pd
import pytest
from pandasai.helpers.logger import Logger

from pandasai.llm.fake import FakeLLM
from pandasai.pipelines.pipeline_context import PipelineContext
from pandasai.smart_dataframe import SmartDataframe
from pandasai.smart_datalake.result_parsing import ResultParsing


class TestResultParsing:
    "Unit test for Smart Data Lake Result Parsing"

    throw_exception = True

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
        return SmartDataframe(sample_df, config={"llm": llm, "enable_cache": True})

    @pytest.fixture
    def config(self, llm):
        return {"llm": llm, "enable_cache": True}

    @pytest.fixture
    def context(self, sample_df, config):
        pipeline_context = PipelineContext([sample_df], config)
        return pipeline_context

    @pytest.fixture
    def logger(self):
        return Logger(True, False)
    
    def test_init(self, context, config):
        # Test the initialization of the CodeExecution
        result_parsing = ResultParsing()
        assert isinstance(result_parsing, ResultParsing)

    def test_result_parsing_successful_with_no_exceptions(self, context, logger):
        # Test Flow : Code Execution Successful with no exceptions
        result_parsing = ResultParsing()
        result_parsing._add_result_to_memory = Mock()
        mock_response_parser = Mock()
        context._query_exec_tracker = Mock()
        context.query_exec_tracker.execute_func = Mock(return_value="Mocked Parsed Result")

        def mock_intermediate_values(key : str):
            if key == "response_parser" :
                return mock_response_parser
        
        context.get_intermediate_value = Mock(side_effect=mock_intermediate_values)

        result = result_parsing.execute(input="Test Result", context=context, logger=logger)

        assert isinstance(result_parsing, ResultParsing)
        assert result == "Mocked Parsed Result"

    def test_result_parsing_unsuccessful_with_exceptions(self, context, logger):
        # Test Flow : Code Execution Unsuccessful with exceptions
        result_parsing = ResultParsing()
        result_parsing._add_result_to_memory = Mock()
        mock_response_parser = Mock()

        def mock_result_parsing(*args, **kwargs):
            raise Exception("Unit test exception")
        
        context._query_exec_tracker = Mock()
        context.query_exec_tracker.execute_func = Mock(side_effect=mock_result_parsing)

        def mock_intermediate_values(key : str):
            if key == "response_parser" :
                return mock_response_parser
        
        context.get_intermediate_value = Mock(side_effect=mock_intermediate_values)

        result = None
        try:
            result = result_parsing.execute(input="Test Result", context=context, logger=logger)
        except Exception as e:
            assert result == None
        assert isinstance(result_parsing, ResultParsing)
        
