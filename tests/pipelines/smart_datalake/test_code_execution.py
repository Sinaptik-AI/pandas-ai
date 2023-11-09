from typing import Optional
from unittest.mock import Mock
import pandas as pd
import pytest
from pandasai.helpers.code_manager import CodeManager
from pandasai.helpers.logger import Logger
from pandasai.helpers.skills_manager import SkillsManager

from pandasai.llm.fake import FakeLLM
from pandasai.pipelines.pipeline_context import PipelineContext
from pandasai.smart_dataframe import SmartDataframe
from pandasai.smart_datalake.code_execution import CodeExecution


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

        def mock_intermediate_values(key : str):
            if key == "last_prompt_id" :
                return "Mocked Promt ID"
            elif key == "skills" :
                return SkillsManager()
            elif key == "code_manager":
                return mock_code_manager   
        context.get_intermediate_value = Mock(side_effect=mock_intermediate_values)

        result = code_execution.execute(input="Test Code", context=context, logger=logger)

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
        context.query_exec_tracker.execute_func = Mock(return_value=["Interuppted Code", "Exception Testing","Unsuccessful after Retries"])

        def mock_intermediate_values(key : str):
            if key == "last_prompt_id" :
                return "Mocked Promt ID"
            elif key == "skills" :
                return SkillsManager()
            elif key == "code_manager":
                return mock_code_manager

        context.get_intermediate_value = Mock(side_effect=mock_intermediate_values)

        assert isinstance(code_execution, CodeExecution)

        result = None
        try:
            result = code_execution.execute(input="Test Code", context=context, logger=logger)
        except Exception as e:
            assert result is None

    def test_code_execution_successful_at_retry(self, context, logger):
        # Test Flow : Code Execution Successful with no exceptions
        code_execution = CodeExecution()

        self.throw_exception == True
        def mock_execute_code(*args, **kwargs):
            if self.throw_exception == True:
                self.throw_exception = False
                raise Exception("Unit test exception")
            return "Mocked Result after retry"

        mock_code_manager = Mock()
        mock_code_manager.execute_code = Mock(side_effect=mock_execute_code)

        context._query_exec_tracker = Mock()
        context.query_exec_tracker.execute_func = Mock(return_value=["Interuppted Code", "Exception Testing","Successful after Retry"])

        def mock_intermediate_values(key : str):
            if key == "last_prompt_id" :
                return "Mocked Promt ID"
            elif key == "skills" :
                return SkillsManager()
            elif key == "code_manager":
                return mock_code_manager
        context.get_intermediate_value = Mock(side_effect=mock_intermediate_values)

        result = code_execution.execute(input="Test Code", context=context, logger=logger)

        assert isinstance(code_execution, CodeExecution)
        assert result == "Mocked Result after retry"
