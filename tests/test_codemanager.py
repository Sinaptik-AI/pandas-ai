"""Unit tests for the CodeManager class"""
import ast
from typing import Optional
from unittest.mock import MagicMock, patch
import uuid

import pandas as pd
import pytest

from pandasai.connectors.sql import (
    PostgreSQLConnector,
    SQLConnector,
    SQLConnectorConfig,
)

from pandasai.exceptions import (
    BadImportError,
    MaliciousQueryError,
    NoCodeFoundError,
    InvalidConfigError,
)
from pandasai.helpers.skills_manager import SkillsManager
from pandasai.llm.fake import FakeLLM

from pandasai.smart_datalake import SmartDatalake

from pandasai.helpers.code_manager import CodeExecutionContext, CodeManager
from pandasai.schemas.df_config import Config
from pandasai.helpers.logger import Logger


class TestCodeManager:
    """Unit tests for the CodeManager class"""

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
    def logger(self):
        return Logger()

    @pytest.fixture
    def config_with_direct_sql(self):
        return Config(
            llm=FakeLLM(output=""),
            enable_cache=False,
            direct_sql=True,
        )

    @pytest.fixture
    def smart_datalake(self, llm, sample_df):
        return SmartDatalake([sample_df], config={"llm": llm, "enable_cache": False})

    @pytest.fixture
    def smart_datalake_with_connector(self, llm, pgsql_connector: PostgreSQLConnector):
        return SmartDatalake(
            [pgsql_connector],
            config={"llm": llm, "enable_cache": False, "direct_sql": True},
        )

    @pytest.fixture
    def code_manager(self, smart_datalake: SmartDatalake):
        return CodeManager(
            dfs=smart_datalake.dfs,
            config=smart_datalake.config,
            logger=smart_datalake.logger,
        )

    @pytest.fixture
    def exec_context(self) -> MagicMock:
        return CodeExecutionContext(uuid.uuid4(), SkillsManager())

    @pytest.fixture
    @patch("pandasai.connectors.sql.create_engine", autospec=True)
    def sql_connector(self, create_engine):
        # Define your ConnectorConfig instance here
        self.config = SQLConnectorConfig(
            dialect="mysql",
            driver="pymysql",
            username="your_username",
            password="your_password",
            host="your_host",
            port=443,
            database="your_database",
            table="your_table",
            where=[["column_name", "=", "value"]],
        ).dict()

        # Create an instance of SQLConnector
        return SQLConnector(self.config)

    @pytest.fixture
    @patch("pandasai.connectors.sql.create_engine", autospec=True)
    def pgsql_connector(self, create_engine):
        # Define your ConnectorConfig instance here
        self.config = SQLConnectorConfig(
            dialect="mysql",
            driver="pymysql",
            username="your_username",
            password="your_password",
            host="your_host",
            port=443,
            database="your_database",
            table="your_table",
            where=[["column_name", "=", "value"]],
        ).dict()

        # Create an instance of SQLConnector
        return PostgreSQLConnector(self.config, name="your_table")

    def test_run_code_for_calculations(
        self, code_manager: CodeManager, exec_context: MagicMock
    ):
        code = """result = {'type': 'number', 'value': 1 + 1}"""
        assert code_manager.execute_code(code, exec_context)["value"] == 2
        assert code_manager.last_code_executed == code

    def test_run_code_invalid_code(
        self, code_manager: CodeManager, exec_context: MagicMock
    ):
        with pytest.raises(Exception):
            # noinspection PyStatementEffect
            code_manager.execute_code("1+ ", exec_context)["value"]

    def test_clean_code_remove_builtins(
        self, code_manager: CodeManager, exec_context: MagicMock
    ):
        builtins_code = """import set
result = {'type': 'number', 'value': set([1, 2, 3])}"""

        exec_context._can_direct_sql = False
        assert code_manager.execute_code(builtins_code, exec_context)["value"] == {
            1,
            2,
            3,
        }
        assert (
            code_manager.last_code_executed
            == """result = {'type': 'number', 'value': set([1, 2, 3])}"""
        )

    def test_clean_code_removes_jailbreak_code(
        self, code_manager: CodeManager, exec_context: MagicMock
    ):
        malicious_code = """__builtins__['str'].__class__.__mro__[-1].__subclasses__()[140].__init__.__globals__['system']('ls')
print('hello world')"""
        assert (
            code_manager._clean_code(malicious_code, exec_context)
            == """print('hello world')"""
        )

    def test_clean_code_remove_environment_defaults(
        self, code_manager: CodeManager, exec_context: MagicMock
    ):
        pandas_code = """import pandas as pd
print('hello world')
"""
        assert (
            code_manager._clean_code(pandas_code, exec_context)
            == "print('hello world')"
        )

    def test_clean_code_whitelist_import(
        self, code_manager: CodeManager, exec_context: MagicMock
    ):
        """Test that an installed whitelisted library is added to the environment."""
        safe_code = """
import numpy as np
np.array()
"""
        assert code_manager._clean_code(safe_code, exec_context) == "np.array()"

    def test_clean_code_raise_bad_import_error(
        self, code_manager: CodeManager, exec_context: MagicMock
    ):
        malicious_code = """
import os
print(os.listdir())
"""
        with pytest.raises(BadImportError):
            code_manager.execute_code(malicious_code, exec_context)

    def test_remove_dfs_overwrites(
        self, code_manager: CodeManager, exec_context: MagicMock
    ):
        hallucinated_code = """dfs = [pd.DataFrame([1,2,3])]
print(dfs)"""
        assert (
            code_manager._clean_code(hallucinated_code, exec_context)
            == """print(dfs)"""
        )

    @patch(
        "pandasai.pipelines.smart_datalake_chat.code_execution.CodeManager.execute_code",
        autospec=True,
    )
    def test_exception_handling(
        self, mock_execute_code: MagicMock, smart_datalake: SmartDatalake
    ):
        mock_execute_code.side_effect = NoCodeFoundError("No code found in the answer.")
        result = smart_datalake.chat("How many countries are in the dataframe?")
        assert result == (
            "Unfortunately, I was not able to answer your question, "
            "because of the following error:\n"
            "\nNo code found in the answer.\n"
        )
        assert smart_datalake.last_error == "No code found in the answer."

    def test_custom_whitelisted_dependencies(
        self, code_manager: CodeManager, llm, exec_context: MagicMock
    ):
        code = """
import my_custom_library
my_custom_library.do_something()
"""
        llm._output = code

        with pytest.raises(BadImportError):
            code_manager._clean_code(code, exec_context)

        code_manager._config.custom_whitelisted_dependencies = ["my_custom_library"]
        assert (
            code_manager._clean_code(code, exec_context)
            == """my_custom_library.do_something()"""
        )

    def test_get_environment(self, code_manager: CodeManager):
        code_manager._additional_dependencies = [
            {"name": "pyplot", "alias": "plt", "module": "matplotlib"},
            {"name": "numpy", "alias": "np", "module": "numpy"},
        ]

        assert "pd" in code_manager._get_environment()
        assert "plt" in code_manager._get_environment()
        assert "np" in code_manager._get_environment()
        assert code_manager._get_environment()["__builtins__"] == {
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
    def test_extract_filters_col_index(self, df_name, code_manager: CodeManager):
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
        filters = code_manager._extract_filters(code)
        assert isinstance(filters, dict)
        assert "dfs[0]" in filters
        assert isinstance(filters["dfs[0]"], list)
        assert len(filters["dfs[0]"]) == 2

        assert filters["dfs[0]"][0] == ("loan_status", "=", "PAIDOFF")
        assert filters["dfs[0]"][1] == ("Gender", "=", "male")

    def test_extract_filters_col_index_multiple_df(self, code_manager: CodeManager):
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
        filters = code_manager._extract_filters(code)
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

    def test_validate_true_direct_sql_with_two_different_connector(
        self, code_manager: CodeManager, sql_connector, pgsql_connector
    ):
        # not exception is raised using single connector
        # raise exception when two different connector
        with pytest.raises(InvalidConfigError):
            code_manager._config.direct_sql = True
            code_manager._validate_direct_sql([sql_connector, pgsql_connector])

    def test_clean_code_direct_sql_code(
        self, exec_context: MagicMock, smart_datalake_with_connector
    ):
        """Test that the direct SQL function definition is removed when 'direct_sql' is True"""
        code_manager = CodeManager(
            dfs=smart_datalake_with_connector.dfs,
            config=smart_datalake_with_connector.config,
            logger=smart_datalake_with_connector.logger,
        )
        safe_code = """
import numpy as np
def execute_sql_query(sql_query: str) -> pd.DataFrame:
    # code to connect to the database and execute the query
    # ...
    # return the result as a dataframe
    return pd.DataFrame()
np.array()
"""
        assert code_manager._clean_code(safe_code, exec_context) == "np.array()"

    def test_clean_code_direct_sql_code_false(
        self, exec_context: MagicMock, code_manager
    ):
        """Test that the direct SQL function definition is removed when 'direct_sql' is False"""
        safe_code = """
import numpy as np
def execute_sql_query(sql_query: str) -> pd.DataFrame:
    # code to connect to the database and execute the query
    # ...
    # return the result as a dataframe
    return pd.DataFrame()
np.array()
"""
        assert (
            code_manager._clean_code(safe_code, exec_context)
            == """def execute_sql_query(sql_query: str) ->pd.DataFrame:
    return pd.DataFrame()


np.array()"""
        )

    def test_check_is_query_using_relevant_table_invalid_query(
        self, code_manager: CodeManager
    ):
        mock_node = ast.parse("sql_query = 'SELECT * FROM your_table'").body[0]

        irrelevant_tables = code_manager._get_sql_irrelevant_tables(mock_node)

        assert len(irrelevant_tables) > 0

    def test_check_is_query_using_relevant_table_valid_query(
        self, code_manager: CodeManager
    ):
        mock_node = ast.parse("sql_query = 'SELECT * FROM allowed_table'").body[0]

        class MockObject:
            name = "allowed_table"

        code_manager._dfs = [MockObject()]

        irrelevant_tables = code_manager._get_sql_irrelevant_tables(mock_node)

        assert len(irrelevant_tables) == 0

    def test_check_is_query_using_relevant_table_multiple_tables(
        self, code_manager: CodeManager
    ):
        mock_node = ast.parse(
            "sql_query = 'SELECT * FROM table1 INNER JOIN table2 ON table1.id = table2.id'"
        ).body[0]

        class MockObject:
            table_name = "allowed_table"

            def __init__(self, table_name):
                self.name = table_name

        code_manager._dfs = [MockObject("table1"), MockObject("table2")]

        irrelevant_tables = code_manager._get_sql_irrelevant_tables(mock_node)

        assert len(irrelevant_tables) == 0

    def test_check_is_query_using_relevant_table_unknown_table(
        self, code_manager: CodeManager
    ):
        mock_node = ast.parse("sql_query = 'SELECT * FROM unknown_table'").body[0]

        class MockObject:
            name = "allowed_table"

        code_manager._dfs = [MockObject()]

        irrelevant_tables = code_manager._get_sql_irrelevant_tables(mock_node)

        assert len(irrelevant_tables) == 1

    def test_check_is_query_using_relevant_table_multiple_tables_one_unknown(
        self, code_manager: CodeManager
    ):
        mock_node = ast.parse(
            "sql_query = 'SELECT * FROM table1 INNER JOIN table2 ON table1.id = table2.id'"
        ).body[0]

        class MockObject:
            table_name = "allowed_table"

            def __init__(self, table_name):
                self.name = table_name

        code_manager._dfs = [MockObject("table1"), MockObject("unknown_table")]

        irrelevant_tables = code_manager._get_sql_irrelevant_tables(mock_node)

        assert len(irrelevant_tables) == 1

    def test_clean_code_using_correct_sql_table(
        self,
        pgsql_connector: PostgreSQLConnector,
        exec_context: MagicMock,
        config_with_direct_sql: Config,
        logger: Logger,
    ):
        """Test that the direct SQL function definition is removed when 'direct_sql' is False"""
        code_manager = CodeManager([pgsql_connector], config_with_direct_sql, logger)
        safe_code = """sql_query = 'SELECT * FROM your_table'"""
        assert code_manager._clean_code(safe_code, exec_context) == safe_code

    def test_clean_code_using_incorrect_sql_table(
        self,
        pgsql_connector: PostgreSQLConnector,
        exec_context: MagicMock,
        config_with_direct_sql: Config,
        logger,
    ):
        """Test that the direct SQL function definition is removed when 'direct_sql' is False"""
        code_manager = CodeManager([pgsql_connector], config_with_direct_sql, logger)
        safe_code = """sql_query = 'SELECT * FROM unknown_table'
    """
        with pytest.raises(MaliciousQueryError) as excinfo:
            code_manager._clean_code(safe_code, exec_context)

        assert str(excinfo.value) == (
            "Query uses unauthorized tables: ['unknown_table']. Please add them as new datatables or update the query."
        )

    def test_clean_code_using_multi_incorrect_sql_table(
        self,
        pgsql_connector: PostgreSQLConnector,
        exec_context: MagicMock,
        config_with_direct_sql: Config,
        logger: Logger,
    ):
        """Test that the direct SQL function definition is removed when 'direct_sql' is False"""
        code_manager = CodeManager([pgsql_connector], config_with_direct_sql, logger)
        safe_code = """sql_query = 'SELECT * FROM table1 INNER JOIN table2 ON table1.id = table2.id'"""
        with pytest.raises(MaliciousQueryError) as excinfo:
            code_manager._clean_code(safe_code, exec_context)

        assert str(excinfo.value) == (
            "Query uses unauthorized tables: ['table1', 'table2']. Please add them as new datatables or update the query."
        )
