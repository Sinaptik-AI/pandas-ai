from typing import Optional
from unittest.mock import Mock

import pandas as pd
import pytest
from pandasai.exceptions import InvalidOutputValueMismatch

from pandasai.helpers.logger import Logger
from pandasai.helpers.skills_manager import SkillsManager
from pandasai.llm.fake import FakeLLM
from pandasai.pipelines.chat.code_execution import CodeExecution
from pandasai.pipelines.pipeline_context import PipelineContext


class TestCodeExecution:
    "Unit test for Code Execution"

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

        context.get = Mock(side_effect=mock_intermediate_values)
        # context._query_exec_tracker = Mock()
        # context.query_exec_tracker.execute_func = Mock(return_value="Mocked Result")

        result = code_execution.execute(
            input='result={"type":"string", "value":"5"}',
            context=context,
            logger=logger,
        )

        assert isinstance(code_execution, CodeExecution)
        assert result.output == {"type": "string", "value": "5"}
        assert result.message == "Code Executed Successfully"
        assert result.success is True

    def test_code_execution_unsuccessful_after_retries(self, context, logger):
        # Test Flow : Code Execution Successful after retry
        code_execution = CodeExecution()

        def mock_execute_code(*args, **kwargs):
            raise Exception("Unit test exception")

        mock_code_manager = Mock()
        mock_code_manager.execute_code = Mock(side_effect=mock_execute_code)

        def mock_intermediate_values(key: str):
            if key == "last_prompt_id":
                return "Mocked Prompt ID"
            elif key == "skills":
                return SkillsManager()
            elif key == "code_manager":
                return mock_code_manager

        context.get = Mock(side_effect=mock_intermediate_values)

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
            return mock_execute_code(*args, **kwargs)

        mock_code_manager = Mock()
        mock_code_manager.execute_code = mock_execute_func
        mock_code_manager.execute_code.name = "execute_code"

        code_execution._retry_run_code = Mock(
            return_value='result={"type":"string", "value":"5"}'
        )

        result = code_execution.execute(input="x=5", context=context, logger=logger)

        assert code_execution._retry_run_code.assert_called
        assert isinstance(code_execution, CodeExecution)
        assert result.output == {"type": "string", "value": "5"}
        assert result.message == "Code Executed Successfully"
        assert result.success is True

    def test_code_execution_output_type_mismatch(self, context, logger):
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

        context.get = Mock(side_effect=mock_intermediate_values)
        # context._query_exec_tracker = Mock()
        # context.query_exec_tracker.execute_func = Mock(return_value="Mocked Result")

        with pytest.raises(InvalidOutputValueMismatch):
            code_execution.execute(
                input='result={"type":"string", "value":5}',
                context=context,
                logger=logger,
            )

    def test_code_execution_output_is_not_dict(self, context, logger):
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

        context.get = Mock(side_effect=mock_intermediate_values)
        # context._query_exec_tracker = Mock()
        # context.query_exec_tracker.execute_func = Mock(return_value="Mocked Result")

        with pytest.raises(InvalidOutputValueMismatch):
            code_execution.execute(
                input="result=5",
                context=context,
                logger=logger,
            )
