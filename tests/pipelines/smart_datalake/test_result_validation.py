from typing import Optional
from unittest.mock import Mock
import pandas as pd
import pytest
from pandasai.helpers.logger import Logger

from pandasai.llm.fake import FakeLLM
from pandasai.pipelines.pipeline_context import PipelineContext
from pandasai.pipelines.smart_datalake_chat.result_validation import ResultValidation


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
    def config(self, llm):
        return {"llm": llm, "enable_cache": True}

    @pytest.fixture
    def context(self, sample_df, config):
        return PipelineContext([sample_df], config)

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

        result = result_validation.execute(input=None, context=context, logger=logger)

        print(result)

        assert isinstance(result_validation, ResultValidation)
        assert result.output is None

    def test_result_is_not_of_dict_type(self, context, logger):
        # Test Flow : Code Execution Successful with no exceptions
        result_validation = ResultValidation()

        result = result_validation.execute(
            input="Not Dict Type Result", context=context, logger=logger
        )

        assert isinstance(result_validation, ResultValidation)
        assert result.output == "Not Dict Type Result"
        assert result.success is False
        assert result.message is None

    def test_result_is_of_dict_type_and_valid(self, context, logger):
        # Test Flow : Code Execution Successful with no exceptions
        result_validation = ResultValidation()
        output_type_helper = Mock()

        context.get = Mock(return_value=output_type_helper)
        output_type_helper.validate = Mock(return_value=(True, "Mocked Logs"))

        result = result_validation.execute(
            input={"Mocked": "Result"}, context=context, logger=logger
        )

        assert isinstance(result_validation, ResultValidation)
        assert result.output == {"Mocked": "Result"}
        assert result.success is True
        assert result.message == "Output Validation Successful"

    def test_result_is_of_dict_type_and_not_valid(self, context, logger):
        # Test Flow : Code Execution Successful with no exceptions
        result_validation = ResultValidation()
        output_type_helper = Mock()

        context.get = Mock(return_value=output_type_helper)
        output_type_helper.validate = Mock(return_value=(False, "Mocked Logs"))

        result = result_validation.execute(
            input={"Mocked": "Result"}, context=context, logger=logger
        )

        assert isinstance(result_validation, ResultValidation)
        assert result.output == {"Mocked": "Result"}
        assert result.success is False
        assert result.message == "Output Validation Failed"
