from typing import Optional
from unittest.mock import Mock
import pandas as pd
import pytest
from pandasai.helpers.logger import Logger

from pandasai.llm.fake import FakeLLM
from pandasai.pipelines.pipeline_context import PipelineContext
from pandasai.smart_dataframe import SmartDataframe
from pandasai.smart_datalake.result_validation import ResultValidation


class TestResultValidation:
    "Unit test for Smart Data Lake Result Validation"

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
        result_validation = ResultValidation()
        assert isinstance(result_validation, ResultValidation)

    def test_result_is_none(self, context, logger):
        # Test Flow : Code Execution Successful with no exceptions
        result_validation = ResultValidation()

        context._query_exec_tracker = Mock()
        context.query_exec_tracker.get_execution_time = Mock()
        context.query_exec_tracker.add_step = Mock()

        result = result_validation.execute(input=None, context=context, logger=logger)

        assert not context.query_exec_tracker.add_step.called
        assert isinstance(result_validation, ResultValidation)
        assert result == None

    def test_result_is_not_of_dict_type(self, context, logger):
        # Test Flow : Code Execution Successful with no exceptions
        result_validation = ResultValidation()

        context._query_exec_tracker = Mock()
        context.query_exec_tracker.get_execution_time = Mock()
        context.query_exec_tracker.add_step = Mock()

        result = result_validation.execute(input="Not Dict Type Result", context=context, logger=logger)

        assert not context.query_exec_tracker.add_step.called
        assert isinstance(result_validation, ResultValidation)
        assert result == "Not Dict Type Result"

    def test_result_is_of_dict_type_and_valid(self, context, logger):
        # Test Flow : Code Execution Successful with no exceptions
        result_validation = ResultValidation()
        output_type_helper = Mock()

        context._query_exec_tracker = Mock()
        context.query_exec_tracker.get_execution_time = Mock()
        context.get_intermediate_value = Mock(return_value=output_type_helper)
        output_type_helper.validate = Mock(return_value=(True,"Mocked Logs"))

        result = result_validation.execute(input={"Mocked":"Result"}, context=context, logger=logger)

        context.query_exec_tracker.add_step.assert_called_with({
                            "type": "Validating Output",
                            "success": True,
                            "message": "Output Validation Successful",
                        })
        assert isinstance(result_validation, ResultValidation)
        assert result == {"Mocked":"Result"}

    def test_result_is_of_dict_type_and_not_valid(self, context, logger):
        # Test Flow : Code Execution Successful with no exceptions
        result_validation = ResultValidation()
        output_type_helper = Mock()

        context._query_exec_tracker = Mock()
        context.query_exec_tracker.get_execution_time = Mock()
        context.get_intermediate_value = Mock(return_value=output_type_helper)
        output_type_helper.validate = Mock(return_value=(False,"Mocked Logs"))

        result = result_validation.execute(input={"Mocked":"Result"}, context=context, logger=logger)

        context.query_exec_tracker.add_step.assert_called_with({
                            "type": "Validating Output",
                            "success": False,
                            "message": "Output Validation Failed",
                        })
        assert isinstance(result_validation, ResultValidation)
        assert result == {"Mocked":"Result"}