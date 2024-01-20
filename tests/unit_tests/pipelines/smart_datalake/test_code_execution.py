from typing import Optional
from unittest.mock import MagicMock, Mock

import pandas as pd
import pytest

from pandasai.exceptions import InvalidLLMOutputType
from pandasai.helpers.logger import Logger
from pandasai.helpers.skills_manager import SkillsManager
from pandasai.llm.fake import FakeLLM
from pandasai.pipelines.pipeline_context import PipelineContext
from pandasai.pipelines.smart_datalake_chat.code_execution import CodeExecution
from pandasai.prompts.correct_error_prompt import CorrectErrorPrompt
from pandasai.prompts.correct_output_type_error_prompt import (
    CorrectOutputTypeErrorPrompt,
)
from pandasai.smart_dataframe import SmartDataframe


class TestCodeExecution:
    "Unit test for Smart Data Lake Code Execution"

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
        return PipelineContext([sample_df], config)

    @pytest.fixture
    def logger(self):
        return Logger(True, False)

    def test_init(self, context, config):
        # Test the initialization of the CodeExecution
        code_execution = CodeExecution()
        assert isinstance(code_execution, CodeExecution)

    def test_code_execution_successful_with_no_exceptions(self, context, logger):
        # Test Flow : Code Execution Successful with no exceptions
        code_execution = CodeExecution()

        mock_code_manager = Mock()
        mock_code_manager.execute_code = Mock(return_value="Mocked Result")

        def mock_intermediate_values(key: str):
            if key == "last_prompt_id":
                return "Mocked Prompt ID"
            elif key == "skills":
                return SkillsManager()
            elif key == "code_manager":
                return mock_code_manager

        context.get_intermediate_value = Mock(side_effect=mock_intermediate_values)
        context._query_exec_tracker = Mock()
        context.query_exec_tracker.execute_func = Mock(return_value="Mocked Result")

        result = code_execution.execute(
            input="Test Code", context=context, logger=logger
        )

        assert isinstance(code_execution, CodeExecution)
        assert result == "Mocked Result"

    def test_code_execution_unsuccessful_after_retries(self, context, logger):
        # Test Flow : Code Execution Successful after retry
        code_execution = CodeExecution()

        def mock_execute_code(*args, **kwargs):
            raise Exception("Unit test exception")

        mock_code_manager = Mock()
        mock_code_manager.execute_code = Mock(side_effect=mock_execute_code)

        context._query_exec_tracker = Mock()
        context.query_exec_tracker.execute_func = Mock(
            return_value=[
                "Interuppted Code",
                "Exception Testing",
                "Unsuccessful after Retries",
            ]
        )

        def mock_intermediate_values(key: str):
            if key == "last_prompt_id":
                return "Mocked Prompt ID"
            elif key == "skills":
                return SkillsManager()
            elif key == "code_manager":
                return mock_code_manager

        context.get_intermediate_value = Mock(side_effect=mock_intermediate_values)

        assert isinstance(code_execution, CodeExecution)

        result = None
        try:
            result = code_execution.execute(
                input="Test Code", context=context, logger=logger
            )
        except Exception:
            assert result is None

    def test_code_execution_successful_at_retry(self, context, logger):
        # Test Flow : Code Execution Successful with no exceptions
        code_execution = CodeExecution()

        def mock_execute_code(*args, **kwargs):
            if self.throw_exception is True:
                self.throw_exception = False
                raise Exception("Unit test exception")
            return "Mocked Result after retry"

        # Conditional return of execute_func method based arguments it is called with
        def mock_execute_func(*args, **kwargs):
            if isinstance(args[0], Mock) and args[0].name == "execute_code":
                return mock_execute_code(*args, **kwargs)
            else:
                return [
                    "Interuppted Code",
                    "Exception Testing",
                    "Successful after Retry",
                ]

        mock_code_manager = Mock()
        mock_code_manager.execute_code = Mock()
        mock_code_manager.execute_code.name = "execute_code"

        context._query_exec_tracker = Mock()

        context.query_exec_tracker.execute_func = Mock(side_effect=mock_execute_func)

        def mock_intermediate_values(key: str):
            if key == "last_prompt_id":
                return "Mocked Prompt ID"
            elif key == "skills":
                return SkillsManager()
            elif key == "code_manager":
                return mock_code_manager

        context.get_intermediate_value = Mock(side_effect=mock_intermediate_values)

        result = code_execution.execute(
            input="Test Code", context=context, logger=logger
        )

        assert isinstance(code_execution, CodeExecution)
        assert result == "Mocked Result after retry"

    def test_get_error_prompt_invalid_llm_output_type(self):
        code_execution = CodeExecution()

        # Mock the InvalidLLMOutputType exception
        mock_exception = MagicMock(spec=InvalidLLMOutputType)

        # Call the method with the mock exception
        result = code_execution._get_error_prompt(mock_exception)

        # Assert that the CorrectOutputTypeErrorPrompt is returned
        assert isinstance(result, CorrectOutputTypeErrorPrompt)

    def test_get_error_prompt_other_exception(self):
        code_execution = CodeExecution()

        # Mock a generic exception
        mock_exception = MagicMock(spec=Exception)

        # Call the method with the mock exception
        result = code_execution._get_error_prompt(mock_exception)

        # Assert that the CorrectErrorPrompt is returned
        assert isinstance(result, CorrectErrorPrompt)
