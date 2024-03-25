import os
from typing import Optional
from unittest.mock import MagicMock, Mock, patch

import pandas as pd
import pytest

from pandasai.agent.base import Agent
from pandasai.exceptions import InvalidOutputValueMismatch, NoCodeFoundError
from pandasai.helpers.logger import Logger
from pandasai.helpers.optional import get_environment
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
    def agent(self, llm, sample_df):
        return Agent([sample_df], config={"llm": llm, "enable_cache": False})

    @pytest.fixture
    def config(self, llm):
        return {"llm": llm, "enable_cache": True}

    @pytest.fixture
    def code(self, llm):
        return {"llm": llm, "enable_cache": True}

    @pytest.fixture
    def context(self, sample_df, config):
        return PipelineContext([sample_df], config)

    @pytest.fixture
    def logger(self):
        return Logger(True, False)

    @pytest.fixture
    def code_execution(self):
        return CodeExecution()

    def test_init(self, context, config):
        # Test the initialization of the CodeExecution
        code_execution = CodeExecution()
        assert isinstance(code_execution, CodeExecution)

    def test_code_execution_successful_with_no_exceptions(self, context, logger):
        # Test Flow : Code Execution Successful with no exceptions
        code_execution = CodeExecution()

        mock_code_manager = Mock()
        mock_code_manager.execute_code = Mock(return_value="Mocked Result")

        def mock_intermediate_values(key: str, default=None):
            if key == "last_prompt_id":
                return "Mocked Prompt ID"
            elif key == "skills":
                return SkillsManager()
            elif key == "code_manager":
                return mock_code_manager
            elif key == "additional_dependencies":
                return []

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

    @pytest.mark.skip(reason="Removed CodeManager class")
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

        def mock_intermediate_values(key: str, default=None):
            if key == "last_prompt_id":
                return "Mocked Prompt ID"
            elif key == "skills":
                return SkillsManager()
            elif key == "code_manager":
                return mock_code_manager
            elif key == "additional_dependencies":
                return []

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

        def mock_intermediate_values(key: str, default=None):
            if key == "last_prompt_id":
                return "Mocked Prompt ID"
            elif key == "skills":
                return SkillsManager()
            elif key == "code_manager":
                return mock_code_manager
            elif key == "additional_dependencies":
                return []

        context.get = Mock(side_effect=mock_intermediate_values)
        # context._query_exec_tracker = Mock()
        # context.query_exec_tracker.execute_func = Mock(return_value="Mocked Result")

        with pytest.raises(InvalidOutputValueMismatch):
            code_execution.execute(
                input="result=5",
                context=context,
                logger=logger,
            )

    @patch(
        "pandasai.pipelines.chat.code_execution.CodeExecution.execute_code",
        autospec=True,
    )
    def test_exception_handling(self, mock_execute_code: MagicMock, agent: Agent):
        os.environ["PANDASAI_API_URL"] = ""
        os.environ["PANDASAI_API_KEY"] = ""

        mock_execute_code.side_effect = NoCodeFoundError("No code found in the answer.")
        result = agent.chat("How many countries are in the dataframe?")
        assert result == (
            "Unfortunately, I was not able to answer your question, "
            "because of the following error:\n"
            "\nNo code found in the answer.\n"
        )
        assert agent.last_error == "No code found in the answer."

    def test_get_environment(self):
        additional_dependencies = [
            {"name": "pyplot", "alias": "plt", "module": "matplotlib"},
            {"name": "numpy", "alias": "np", "module": "numpy"},
        ]
        environment = get_environment(additional_dependencies)

        assert "pd" in environment
        assert "plt" in environment
        assert "np" in environment
        assert environment["__builtins__"] == {
            "abs": abs,
            "all": all,
            "any": any,
            "ascii": ascii,
            "bin": bin,
            "bool": bool,
            "bytearray": bytearray,
            "bytes": bytes,
            "callable": callable,
            "chr": chr,
            "classmethod": classmethod,
            "complex": complex,
            "delattr": delattr,
            "dict": dict,
            "dir": dir,
            "divmod": divmod,
            "enumerate": enumerate,
            "filter": filter,
            "float": float,
            "format": format,
            "frozenset": frozenset,
            "getattr": getattr,
            "hasattr": hasattr,
            "hash": hash,
            "help": help,
            "hex": hex,
            "id": id,
            "int": int,
            "isinstance": isinstance,
            "issubclass": issubclass,
            "iter": iter,
            "len": len,
            "list": list,
            "locals": locals,
            "map": map,
            "max": max,
            "memoryview": memoryview,
            "min": min,
            "next": next,
            "object": object,
            "oct": oct,
            "ord": ord,
            "pow": pow,
            "print": print,
            "property": property,
            "range": range,
            "repr": repr,
            "reversed": reversed,
            "round": round,
            "set": set,
            "setattr": setattr,
            "slice": slice,
            "sorted": sorted,
            "staticmethod": staticmethod,
            "str": str,
            "sum": sum,
            "super": super,
            "tuple": tuple,
            "type": type,
            "vars": vars,
            "zip": zip,
            "__build_class__": __build_class__,
            "__name__": "__main__",
        }

    @pytest.mark.parametrize("df_name", ["df", "foobar"])
    def test_extract_filters_col_index(self, df_name, code_execution):
        code = f"""
{df_name} = dfs[0]
filtered_df = (
    {df_name}[
        ({df_name}['loan_status'] == 'PAIDOFF') & ({df_name}['Gender'] == 'male')
    ]
)
num_loans = len(filtered_df)
result = {{'type': 'number', 'value': num_loans}}
"""
        filters = code_execution._extract_filters(code)
        assert isinstance(filters, dict)
        assert "dfs[0]" in filters
        assert isinstance(filters["dfs[0]"], list)
        assert len(filters["dfs[0]"]) == 2

        assert filters["dfs[0]"][0] == ("loan_status", "=", "PAIDOFF")
        assert filters["dfs[0]"][1] == ("Gender", "=", "male")

    def test_extract_filters_col_index_multiple_df(self, code_execution, logger):
        code = """
df = dfs[0]
filtered_paid_df_male = df[(
    df['loan_status'] == 'PAIDOFF') & (df['Gender'] == 'male'
)]
num_loans_paid_off_male = len(filtered_paid_df)

df = dfs[1]
filtered_pend_df_male = df[(
    df['loan_status'] == 'PENDING') & (df['Gender'] == 'male'
)]
num_loans_pending_male = len(filtered_pend_df)

df = dfs[2]
filtered_paid_df_female = df[(
    df['loan_status'] == 'PAIDOFF') & (df['Gender'] == 'female'
)]
num_loans_paid_off_female = len(filtered_pend_df)

value = num_loans_paid_off + num_loans_pending + num_loans_paid_off_female
result = {
    'type': 'number',
    'value': value
}
"""
        code_execution.logger = logger
        filters = code_execution._extract_filters(code)
        print(filters)
        assert isinstance(filters, dict)
        assert "dfs[0]" in filters
        assert "dfs[1]" in filters
        assert "dfs[2]" in filters
        assert isinstance(filters["dfs[0]"], list)
        assert len(filters["dfs[0]"]) == 2
        assert len(filters["dfs[1]"]) == 2

        assert filters["dfs[0]"][0] == ("loan_status", "=", "PAIDOFF")
        assert filters["dfs[0]"][1] == ("Gender", "=", "male")

        assert filters["dfs[1]"][0] == ("loan_status", "=", "PENDING")
        assert filters["dfs[1]"][1] == ("Gender", "=", "male")

        assert filters["dfs[2]"][0] == ("loan_status", "=", "PAIDOFF")
        assert filters["dfs[2]"][1] == ("Gender", "=", "female")
