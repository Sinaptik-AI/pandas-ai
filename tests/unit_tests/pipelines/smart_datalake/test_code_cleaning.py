"""Unit tests for the CodeCleaning class"""

import ast
import uuid
from typing import Optional
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from pandasai import Agent
from pandasai.connectors.pandas import PandasConnector
from pandasai.connectors.sql import (
    PostgreSQLConnector,
    SQLConnector,
    SQLConnectorConfig,
)
from pandasai.exceptions import (
    BadImportError,
    InvalidConfigError,
    MaliciousQueryError,
)
from pandasai.helpers.logger import Logger
from pandasai.helpers.skills_manager import SkillsManager
from pandasai.llm.fake import FakeLLM
from pandasai.pipelines.chat.code_cleaning import CodeCleaning, CodeExecutionContext
from pandasai.pipelines.logic_unit_output import LogicUnitOutput
from pandasai.pipelines.pipeline_context import PipelineContext
from pandasai.schemas.df_config import Config


class MockDataframe:
    table_name = "allowed_table"

    def __init__(self, table_name="test"):
        self.name = table_name

    @property
    def cs_table_name(self):
        return self.name


class TestCodeCleaning:
    """Unit tests for the CodeCleaning class"""

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
    def config(self, llm):
        return {"llm": llm, "enable_cache": True}

    @pytest.fixture
    def context(self, sample_df, config):
        return PipelineContext([sample_df], config)

    @pytest.fixture
    def agent(self, llm, sample_df):
        return Agent([sample_df], config={"llm": llm, "enable_cache": False})

    @pytest.fixture
    def agent_with_connector(self, llm, pgsql_connector: PostgreSQLConnector):
        return Agent(
            [pgsql_connector],
            config={"llm": llm, "enable_cache": False, "direct_sql": True},
        )

    @pytest.fixture
    def code_cleaning(self, agent: Agent):
        return CodeCleaning()

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
        self,
        code_cleaning: CodeCleaning,
        context: PipelineContext,
        logger: Logger,
    ):
        code = """result = {'type': 'number', 'value': 1 + 1}"""
        output = code_cleaning.execute(code, context=context, logger=logger)
        assert isinstance(output, LogicUnitOutput)
        assert output.success
        assert output.message == "Code Cleaned Successfully"

    def test_run_code_invalid_code(
        self,
        code_cleaning: CodeCleaning,
        context: PipelineContext,
        logger: Logger,
    ):
        with pytest.raises(Exception):
            code_cleaning.execute("1 +", context=context, logger=logger)

    def test_clean_code_remove_builtins(
        self,
        code_cleaning: CodeCleaning,
        context: PipelineContext,
        logger: Logger,
    ):
        builtins_code = """import set
result = {'type': 'number', 'value': set([1, 2, 3])}"""

        output = code_cleaning.execute(builtins_code, context=context, logger=logger)

        assert (
            output.output == """result = {'type': 'number', 'value': set([1, 2, 3])}"""
        )
        assert isinstance(output, LogicUnitOutput)
        assert output.success
        assert output.message == "Code Cleaned Successfully"

    def test_clean_code_removes_jailbreak_code(
        self,
        code_cleaning: CodeCleaning,
        context: PipelineContext,
        logger: Logger,
    ):
        malicious_code = """__builtins__['str'].__class__.__mro__[-1].__subclasses__()[140].__init__.__globals__['system']('ls')
print('hello world')"""

        output = code_cleaning.execute(malicious_code, context=context, logger=logger)

        assert output.output == """print('hello world')"""
        assert isinstance(output, LogicUnitOutput)
        assert output.success
        assert output.message == "Code Cleaned Successfully"

    def test_clean_code_remove_environment_defaults(
        self,
        code_cleaning: CodeCleaning,
        context: PipelineContext,
        logger: Logger,
    ):
        pandas_code = """import pandas as pd
print('hello world')
"""
        output = code_cleaning.execute(pandas_code, context=context, logger=logger)

        assert output.output == """print('hello world')"""
        assert isinstance(output, LogicUnitOutput)
        assert output.success
        assert output.message == "Code Cleaned Successfully"

    def test_clean_code_whitelist_import(
        self,
        code_cleaning: CodeCleaning,
        context: PipelineContext,
        logger: Logger,
    ):
        """Test that an installed whitelisted library is added to the environment."""
        safe_code = """
import numpy as np
np.array()
"""
        output = code_cleaning.execute(safe_code, context=context, logger=logger)

        assert output.output == """np.array()"""
        assert isinstance(output, LogicUnitOutput)
        assert output.success
        assert output.message == "Code Cleaned Successfully"

    def test_clean_code_raise_bad_import_error(
        self,
        code_cleaning: CodeCleaning,
        context: PipelineContext,
        logger: Logger,
    ):
        malicious_code = """
import os
print(os.listdir())
"""
        with pytest.raises(MaliciousQueryError):
            code_cleaning.execute(malicious_code, context=context, logger=logger)

    def test_clean_code_accesses_node_id(
        self,
        code_cleaning: CodeCleaning,
        context: PipelineContext,
        logger: Logger,
    ):
        """Test that value.func.value.id is accessed safely in _check_is_df_declaration."""
        pandas_code = """unique_countries = dfs[0]['country'].unique()
smallest_countries = df.sort_values(by='area').head()"""
        output = code_cleaning.execute(pandas_code, context=context, logger=logger)

        assert output.output == pandas_code
        assert isinstance(output, LogicUnitOutput)
        assert output.success
        assert output.message == "Code Cleaned Successfully"

    def test_remove_dfs_overwrites(
        self,
        code_cleaning: CodeCleaning,
        context: PipelineContext,
        logger: Logger,
    ):
        hallucinated_code = """dfs = [pd.DataFrame([1,2,3])]
print(dfs)"""
        output = code_cleaning.execute(
            hallucinated_code, context=context, logger=logger
        )

        assert output.output == """print(dfs)"""
        assert isinstance(output, LogicUnitOutput)
        assert output.success
        assert output.message == "Code Cleaned Successfully"

    def test_custom_whitelisted_dependencies(
        self,
        code_cleaning: CodeCleaning,
        context: PipelineContext,
        logger: Logger,
    ):
        code = """
import my_custom_library
my_custom_library.do_something()
"""

        with pytest.raises(BadImportError):
            code_cleaning.execute(code, context=context, logger=logger)

        code_cleaning._config.custom_whitelisted_dependencies = ["my_custom_library"]
        output = code_cleaning.execute(code, context=context, logger=logger)

        assert output.output == "my_custom_library.do_something()"
        assert isinstance(output, LogicUnitOutput)
        assert output.success
        assert output.message == "Code Cleaned Successfully"

    def test_validate_true_direct_sql_with_two_different_connector(
        self,
        code_cleaning: CodeCleaning,
        context: PipelineContext,
        logger: Logger,
        sql_connector,
        pgsql_connector,
    ):
        # not exception is raised using single connector
        # raise exception when two different connector
        with pytest.raises(InvalidConfigError):
            context.config.direct_sql = True
            context.dfs = [sql_connector, pgsql_connector]
            code_cleaning.execute(
                "np.array()\nexecute_sql_query()", context=context, logger=logger
            )

    def test_clean_code_direct_sql_code(
        self,
        code_cleaning: CodeCleaning,
        context: PipelineContext,
        logger: Logger,
        agent_with_connector: Agent,
        sql_connector,
        pgsql_connector,
    ):
        """Test that the direct SQL function definition is removed when 'direct_sql' is True"""
        safe_code = """
import numpy as np
def execute_sql_query(sql_query: str) -> pd.DataFrame:
    # code to connect to the database and execute the query
    # ...
    # return the result as a dataframe
    return pd.DataFrame()
np.array()
execute_sql_query()
"""
        context.config.direct_sql = True
        context.dfs = [pgsql_connector, pgsql_connector]
        output = code_cleaning.execute(safe_code, context=context, logger=logger)

        assert output.output == "np.array()\nexecute_sql_query()"
        assert isinstance(output, LogicUnitOutput)
        assert output.success
        assert output.message == "Code Cleaned Successfully"

    def test_clean_code_direct_sql_code_false(
        self,
        code_cleaning: CodeCleaning,
        context: PipelineContext,
        logger: Logger,
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
        output = code_cleaning.execute(safe_code, context=context, logger=logger)
        assert (
            output.output
            == """def execute_sql_query(sql_query: str) ->pd.DataFrame:
    return pd.DataFrame()


np.array()"""
        )
        assert isinstance(output, LogicUnitOutput)
        assert output.success
        assert output.message == "Code Cleaned Successfully"

    def test_check_is_query_using_relevant_table_invalid_query(
        self, code_cleaning: CodeCleaning
    ):
        mock_node = ast.parse("sql_query = 'SELECT * FROM your_table'").body[0]

        code_cleaning._dfs = [MockDataframe("allowed_table")]

        with pytest.raises(MaliciousQueryError):
            code_cleaning._validate_and_make_table_name_case_sensitive(mock_node)

    def test_check_is_query_using_relevant_table_valid_query(
        self, code_cleaning: CodeCleaning
    ):
        mock_node = ast.parse("sql_query = 'SELECT * FROM allowed_table'").body[0]

        code_cleaning._dfs = [MockDataframe("allowed_table")]

        node = code_cleaning._validate_and_make_table_name_case_sensitive(mock_node)

        assert isinstance(node, ast.Assign)
        assert node.value.value == "SELECT * FROM allowed_table"

    def test_check_is_query_using_relevant_table_multiple_tables(
        self, code_cleaning: CodeCleaning
    ):
        mock_node = ast.parse(
            "sql_query = 'SELECT * FROM table1 INNER JOIN table2 ON table1.id = table2.id'"
        ).body[0]

        code_cleaning._dfs = [MockDataframe("table1"), MockDataframe("table2")]

        node = code_cleaning._validate_and_make_table_name_case_sensitive(mock_node)

        assert isinstance(node, ast.Assign)
        assert (
            node.value.value
            == "SELECT * FROM table1 INNER JOIN table2 ON table1.id = table2.id"
        )

    def test_check_is_query_using_relevant_table_multiple_tables_using_alias_with_quote(
        self, code_cleaning: CodeCleaning
    ):
        mock_node = ast.parse(
            "sql_query = 'SELECT table1.id AS id, table1.author_id, table2.hidden AS is_hidden, table3.text AS comment_text FROM table1 LEFT JOIN table2 ON table1.id = table2.feed_message_id LEFT JOIN table3 ON table1.id = table3.feed_message_id'"
        ).body[0]

        class MockObject:
            table_name = "allowed_table"

            def __init__(self, table_name):
                self.name = table_name

            @property
            def cs_table_name(self):
                return f'"{self.name}"'

        code_cleaning._dfs = [
            MockObject("table1"),
            MockObject("table2"),
            MockObject("table3"),
        ]

        node = code_cleaning._validate_and_make_table_name_case_sensitive(mock_node)

        assert isinstance(node, ast.Assign)
        assert (
            node.value.value
            == 'SELECT "table1".id AS id, "table1".author_id, "table2".hidden AS is_hidden, "table3".text AS comment_text FROM "table1" LEFT JOIN "table2" ON "table1".id = "table2".feed_message_id LEFT JOIN "table3" ON "table1".id = "table3".feed_message_id'
        )

    def test_check_relevant_table_multiple_tables_passing_directly_to_function(
        self, code_cleaning: CodeCleaning
    ):
        mock_node = ast.parse(
            "execute_sql_query('SELECT table1.id AS id, table1.author_id, table2.hidden AS is_hidden, table3.text AS comment_text FROM table1 LEFT JOIN table2 ON table1.id = table2.feed_message_id LEFT JOIN table3 ON table1.id = table3.feed_message_id')"
        ).body[0]

        code_cleaning._dfs = [
            MockDataframe("table1"),
            MockDataframe("table2"),
            MockDataframe("table3"),
        ]

        node = code_cleaning._validate_and_make_table_name_case_sensitive(mock_node)

        assert isinstance(node, ast.Expr)
        assert (
            node.value.args[0].value
            == "SELECT table1.id AS id, table1.author_id, table2.hidden AS is_hidden, table3.text AS comment_text FROM table1 LEFT JOIN table2 ON table1.id = table2.feed_message_id LEFT JOIN table3 ON table1.id = table3.feed_message_id"
        )

    def test_check_is_query_using_relevant_table_unknown_table(
        self, code_cleaning: CodeCleaning
    ):
        mock_node = ast.parse("sql_query = 'SELECT * FROM unknown_table'").body[0]

        code_cleaning._dfs = [MockDataframe()]

        with pytest.raises(MaliciousQueryError):
            code_cleaning._validate_and_make_table_name_case_sensitive(mock_node)

    def test_check_is_query_using_relevant_table_multiple_tables_one_unknown(
        self, code_cleaning: CodeCleaning
    ):
        mock_node = ast.parse(
            "sql_query = 'SELECT * FROM table1 INNER JOIN table2 ON table1.id = table2.id'"
        ).body[0]

        code_cleaning._dfs = [MockDataframe("table1"), MockDataframe("unknown_table")]

        with pytest.raises(MaliciousQueryError):
            code_cleaning._validate_and_make_table_name_case_sensitive(mock_node)

    def test_clean_code_using_correct_sql_table(
        self,
        pgsql_connector: PostgreSQLConnector,
        context: PipelineContext,
        logger: Logger,
    ):
        """Test that the correct sql table"""
        code_cleaning = CodeCleaning()

        context.dfs = [pgsql_connector]
        safe_code = (
            """sql_query = 'SELECT * FROM your_table'\nexecute_sql_query(sql_query)"""
        )
        context.config.direct_sql = True
        output = code_cleaning.execute(safe_code, context=context, logger=logger)
        assert (
            output.output
            == "sql_query = 'SELECT * FROM \"your_table\"'\nexecute_sql_query(sql_query)"
        )
        assert isinstance(output, LogicUnitOutput)
        assert output.success
        assert output.message == "Code Cleaned Successfully"

    def test_clean_code_with_no_execute_sql_query_usage_script(
        self,
        pgsql_connector: PostgreSQLConnector,
        context: PipelineContext,
        logger: Logger,
    ):
        """Test that the correct sql table"""
        code_cleaning = CodeCleaning()
        code_cleaning._dfs = [pgsql_connector]
        safe_code = (
            """orders_count = execute_sql_query('SELECT COUNT(*) FROM orders')[0][0]"""
        )
        output = code_cleaning.execute(safe_code, context=context, logger=logger)
        assert output.output == safe_code
        assert isinstance(output, LogicUnitOutput)
        assert output.success
        assert output.message == "Code Cleaned Successfully"

    def test_clean_code_using_incorrect_sql_table(
        self,
        pgsql_connector: PostgreSQLConnector,
        context: PipelineContext,
        logger,
    ):
        """Test that the direct SQL function definition is removed when 'direct_sql' is False"""
        code_cleaning = CodeCleaning()
        context.dfs = [pgsql_connector]
        context.config.direct_sql = True
        safe_code = """sql_query = 'SELECT * FROM unknown_table'
    """
        with pytest.raises(MaliciousQueryError) as excinfo:
            code_cleaning.execute(safe_code, context=context, logger=logger)

        assert str(excinfo.value) == ("Query uses unauthorized table: unknown_table.")

    def test_clean_code_using_multi_incorrect_sql_table(
        self,
        pgsql_connector: PostgreSQLConnector,
        context: PipelineContext,
        logger: Logger,
    ):
        """Test that the direct SQL function definition is removed when 'direct_sql' is False"""
        code_cleaning = CodeCleaning()
        context.dfs = [pgsql_connector]
        context.config.direct_sql = True
        safe_code = """sql_query = 'SELECT * FROM table1 INNER JOIN table2 ON table1.id = table2.id'"""
        with pytest.raises(MaliciousQueryError) as excinfo:
            code_cleaning.execute(safe_code, context=context, logger=logger)

        assert str(excinfo.value) == ("Query uses unauthorized table: table1.")

    @patch("pandasai.connectors.pandas.PandasConnector.head")
    def test_fix_dataframe_redeclarations(self, mock_head, context: PipelineContext):
        df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        mock_head.return_value = df
        pandas_connector = PandasConnector({"original_df": df})

        code_cleaning = CodeCleaning()
        code_cleaning._dfs = [pandas_connector]
        context.dfs = [pandas_connector]

        python_code = """
df1 = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
"""
        tree = ast.parse(python_code)

        clean_code = ["df1 = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})"]

        output = code_cleaning._extract_fix_dataframe_redeclarations(
            tree.body[0], clean_code
        )

        assert isinstance(output, ast.Assign)

    @patch("pandasai.connectors.pandas.PandasConnector.head")
    def test_fix_dataframe_multiline_redeclarations(
        self, mock_head, context: PipelineContext
    ):
        df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        mock_head.return_value = df
        pandas_connector = PandasConnector({"original_df": df})

        code_cleaning = CodeCleaning()
        code_cleaning._dfs = [pandas_connector]
        context.dfs = [pandas_connector]

        python_code = """
import pandas as pd

df1 = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})

print(df1)
"""
        tree = ast.parse(python_code)
        clean_codes = [
            "df1 = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})",
        ]

        outputs = [
            code_cleaning._extract_fix_dataframe_redeclarations(node, clean_codes)
            for node in tree.body
        ]

        assert outputs[0] is None
        assert outputs[1] is not None
        assert isinstance(outputs[1], ast.Assign)
        assert outputs[2] is None

    @patch("pandasai.connectors.pandas.PandasConnector.head")
    def test_fix_dataframe_no_redeclarations(self, mock_head, context: PipelineContext):
        df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        mock_head.return_value = df
        pandas_connector = PandasConnector({"original_df": df})

        code_cleaning = CodeCleaning()
        code_cleaning._dfs = [pandas_connector]
        context.dfs = [pandas_connector]

        python_code = """
df1 = dfs[0]
"""
        tree = ast.parse(python_code)

        code_list = ["df1 = dfs[0]"]

        output = code_cleaning._extract_fix_dataframe_redeclarations(
            tree.body[0], code_list
        )

        assert output is None

    @patch("pandasai.connectors.pandas.PandasConnector.head")
    def test_fix_dataframe_redeclarations_with_subscript(
        self, mock_head, context: PipelineContext
    ):
        df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        mock_head.return_value = df
        pandas_connector = PandasConnector({"original_df": df})

        code_cleaning = CodeCleaning()
        code_cleaning._dfs = [pandas_connector]
        context.dfs = [pandas_connector]

        python_code = """
dfs[0] = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
"""
        tree = ast.parse(python_code)

        code_list = ["dfs[0] = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})"]

        output = code_cleaning._extract_fix_dataframe_redeclarations(
            tree.body[0], code_list
        )

        assert isinstance(output, ast.Assign)

    @patch("pandasai.connectors.pandas.PandasConnector.head")
    def test_fix_dataframe_redeclarations_with_subscript_and_data_variable(
        self, mock_head, context: PipelineContext
    ):
        data = {
            "country": ["China", "United States", "Japan", "Germany", "United Kingdom"],
            "sales": [8000, 6000, 4000, 3500, 3000],
        }
        df = pd.DataFrame(data)
        mock_head.return_value = df
        pandas_connector = PandasConnector({"original_df": df})

        code_cleaning = CodeCleaning()
        code_cleaning._dfs = [pandas_connector]
        context.dfs = [pandas_connector]

        python_code = """
data = {'country': ['China', 'United States', 'Japan', 'Germany', 'United Kingdom'],
        'sales': [8000, 6000, 4000, 3500, 3000]}
dfs[0] = pd.DataFrame(data)
"""
        tree = ast.parse(python_code)

        code_list = [
            "data = {'country': ['China', 'United States', 'Japan', 'Germany', 'United Kingdom'],'sales': [8000, 6000, 4000, 3500, 3000]}",
            "dfs[0] = pd.DataFrame(data)",
        ]

        output = code_cleaning._extract_fix_dataframe_redeclarations(
            tree.body[1], code_list
        )

        assert isinstance(output, ast.Assign)

    @patch("pandasai.connectors.pandas.PandasConnector.head")
    def test_fix_dataframe_redeclarations_and_data_variable(
        self, mock_head, context: PipelineContext
    ):
        data = {
            "country": ["China", "United States", "Japan", "Germany", "United Kingdom"],
            "sales": [8000, 6000, 4000, 3500, 3000],
        }
        df = pd.DataFrame(data)
        mock_head.return_value = df
        pandas_connector = PandasConnector({"original_df": df})

        code_cleaning = CodeCleaning()
        code_cleaning._dfs = [pandas_connector]
        context.dfs = [pandas_connector]

        python_code = """
data = {'country': ['China', 'United States', 'Japan', 'Germany', 'United Kingdom'],
        'sales': [8000, 6000, 4000, 3500, 3000]}
df = pd.DataFrame(data)
"""
        tree = ast.parse(python_code)

        code_list = [
            "data = {'country': ['China', 'United States', 'Japan', 'Germany', 'United Kingdom'],'sales': [8000, 6000, 4000, 3500, 3000]}",
            "df = pd.DataFrame(data)",
        ]

        output = code_cleaning._extract_fix_dataframe_redeclarations(
            tree.body[1], code_list
        )

        assert isinstance(output, ast.Assign)

    def test_check_is_query_using_quote_with_table_name(
        self, code_cleaning: CodeCleaning
    ):
        mock_node = ast.parse("""sql_query = 'SELECT * FROM "allowed_table"'""").body[0]

        code_cleaning._dfs = [MockDataframe("allowed_table")]

        node = code_cleaning._validate_and_make_table_name_case_sensitive(mock_node)

        assert isinstance(node, ast.Assign)
        assert node.value.value == 'SELECT * FROM "allowed_table"'

    def test_check_is_query_not_extract_created_at(self, code_cleaning: CodeCleaning):
        mock_node = ast.parse(
            """sql_query = 'SELECT EXTRACT(MONTH FROM "created_at"::TIMESTAMP) AS month, COUNT(*) AS user_count FROM "Users" GROUP BY EXTRACT(MONTH FROM "created_at"::TIMESTAMP)'"""
        ).body[0]

        code_cleaning._dfs = [MockDataframe("Users")]

        node = code_cleaning._validate_and_make_table_name_case_sensitive(mock_node)

        assert isinstance(node, ast.Assign)
        assert (
            node.value.value
            == 'SELECT EXTRACT(MONTH FROM "created_at"::TIMESTAMP) AS month, COUNT(*) AS user_count FROM "Users" GROUP BY EXTRACT(MONTH FROM "created_at"::TIMESTAMP)'
        )

    def test_check_is_query_not_extract_without_quote_created_at(
        self, code_cleaning: CodeCleaning
    ):
        mock_node = ast.parse(
            """sql_query = 'SELECT EXTRACT(MONTH FROM "created_at"::TIMESTAMP) AS month, COUNT(*) AS user_count FROM Users GROUP BY EXTRACT(MONTH FROM "created_at"::TIMESTAMP)'"""
        ).body[0]

        code_cleaning._dfs = [MockDataframe("Users")]

        node = code_cleaning._validate_and_make_table_name_case_sensitive(mock_node)

        assert isinstance(node, ast.Assign)
        assert (
            node.value.value
            == 'SELECT EXTRACT(MONTH FROM "created_at"::TIMESTAMP) AS month, COUNT(*) AS user_count FROM Users GROUP BY EXTRACT(MONTH FROM "created_at"::TIMESTAMP)'
        )

    def test_check_is_query_not_extract_postgres_without_quote_created_at(
        self, code_cleaning: CodeCleaning
    ):
        mock_node = ast.parse(
            """sql_query = 'SELECT EXTRACT(MONTH FROM "created_at"::TIMESTAMP) AS month, COUNT(*) AS user_count FROM Users GROUP BY EXTRACT(MONTH FROM "created_at"::TIMESTAMP)'"""
        ).body[0]

        class MockObject:
            table_name = "allowed_table"

            def __init__(self, table_name):
                self.name = table_name

            @property
            def cs_table_name(self):
                return f'"{self.name}"'

        code_cleaning._dfs = [MockObject("Users")]

        node = code_cleaning._validate_and_make_table_name_case_sensitive(mock_node)

        assert isinstance(node, ast.Assign)
        assert (
            node.value.value
            == 'SELECT EXTRACT(MONTH FROM "created_at"::TIMESTAMP) AS month, COUNT(*) AS user_count FROM "Users" GROUP BY EXTRACT(MONTH FROM "created_at"::TIMESTAMP)'
        )

    def test_check_query_with_semicolon(self, code_cleaning: CodeCleaning):
        mock_node = ast.parse(
            """sql_query = 'SELECT COUNT(*) AS user_count FROM Users;'"""
        ).body[0]

        class MockObject:
            table_name = "allowed_table"

            def __init__(self, table_name):
                self.name = table_name

            @property
            def cs_table_name(self):
                return f'"{self.name}"'

        code_cleaning._dfs = [MockObject("Users")]

        node = code_cleaning._validate_and_make_table_name_case_sensitive(mock_node)

        assert isinstance(node, ast.Assign)
        assert node.value.value == 'SELECT COUNT(*) AS user_count FROM "Users"'

    def test_check_query_with_semicolon_execute_sql_func(
        self, code_cleaning: CodeCleaning
    ):
        mock_node = ast.parse(
            """df=execute_sql_query('SELECT COUNT(*) AS user_count FROM Users;')"""
        ).body[0]

        class MockObject:
            table_name = "allowed_table"

            def __init__(self, table_name):
                self.name = table_name

            @property
            def cs_table_name(self):
                return f'"{self.name}"'

        code_cleaning._dfs = [MockObject("Users")]

        node = code_cleaning._validate_and_make_table_name_case_sensitive(mock_node)

        assert isinstance(node, ast.Assign)
        assert node.value.args[0].value == 'SELECT COUNT(*) AS user_count FROM "Users"'

    def test_check_query_with_semicolon_execute_sql_func_no_assign(
        self, code_cleaning: CodeCleaning
    ):
        mock_node = ast.parse(
            """execute_sql_query('SELECT COUNT(*) AS user_count FROM Users;')"""
        ).body[0]

        class MockObject:
            table_name = "allowed_table"

            def __init__(self, table_name):
                self.name = table_name

            @property
            def cs_table_name(self):
                return f'"{self.name}"'

        code_cleaning._dfs = [MockObject("Users")]

        node = code_cleaning._validate_and_make_table_name_case_sensitive(mock_node)

        assert node.value.args[0].value == 'SELECT COUNT(*) AS user_count FROM "Users"'
