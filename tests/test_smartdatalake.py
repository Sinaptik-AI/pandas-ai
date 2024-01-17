"""Unit tests for the SmartDatalake class"""
import os
import sys

from typing import Optional
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from pandasai import SmartDataframe, SmartDatalake
from pandasai.connectors.sql import (
    PostgreSQLConnector,
    SQLConnector,
    SQLConnectorConfig,
)
from pandasai.helpers.code_manager import CodeManager
from pandasai.llm.fake import FakeLLM
from pandasai.constants import DEFAULT_FILE_PERMISSIONS

from langchain import OpenAI
from pandasai.llm.langchain import LangchainLLM


class TestSmartDatalake:
    """Unit tests for the SmartDatlake class"""

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
        return PostgreSQLConnector(self.config)

    @pytest.fixture
    def smart_dataframe(self, llm, sample_df):
        return SmartDataframe(sample_df, config={"llm": llm, "enable_cache": False})

    @pytest.fixture
    def smart_datalake(self, smart_dataframe: SmartDataframe):
        return smart_dataframe.lake

    def test_load_llm_with_pandasai_llm(self, smart_datalake: SmartDatalake, llm):
        assert smart_datalake.load_llm(llm) == llm

    def test_load_llm_with_langchain_llm(self, smart_datalake: SmartDatalake, llm):
        langchain_llm = OpenAI(openai_api_key="fake_key")

        llm = smart_datalake.load_llm(langchain_llm)
        assert isinstance(llm, LangchainLLM)
        assert llm.langchain_llm == langchain_llm

    @patch.object(
        CodeManager,
        "execute_code",
        return_value={
            "type": "string",
            "value": "There are 10 countries in the dataframe.",
        },
    )
    def test_last_result_is_saved(self, _mocked_method, smart_datalake: SmartDatalake):
        assert smart_datalake.last_result is None

        _mocked_method.__name__ = "execute_code"

        smart_datalake.chat("How many countries are in the dataframe?")
        assert smart_datalake.last_result == {
            "type": "string",
            "value": "There are 10 countries in the dataframe.",
        }

    @patch.object(
        CodeManager,
        "execute_code",
        return_value={
            "type": "string",
            "value": "There are 10 countries in the dataframe.",
        },
    )
    @patch("pandasai.helpers.query_exec_tracker.QueryExecTracker.publish")
    def test_query_tracker_publish_called_in_chat_method(
        self, mock_query_tracker_publish, _mocked_method, smart_datalake: SmartDatalake
    ):
        assert smart_datalake.last_result is None

        _mocked_method.__name__ = "execute_code"

        smart_datalake.chat("How many countries are in the dataframe?")
        mock_query_tracker_publish.assert_called()

    @patch(
        "pandasai.pipelines.smart_datalake_chat.code_execution.CodeManager.execute_code",
        autospec=True,
    )
    @patch(
        "pandasai.pipelines.smart_datalake_chat.code_generator.CodeGenerator.execute",
        autospec=True,
    )
    @patch(
        "pandasai.pipelines.smart_datalake_chat.code_execution.traceback.format_exc",
        autospec=True,
    )
    def test_retry_on_error_with_single_df(
        self,
        mock_traceback,
        mock_generate,
        mock_execute,
        smart_datalake: SmartDatalake,
        smart_dataframe: SmartDataframe,
    ):
        mock_traceback.return_value = "Test error"
        mock_generate.return_value = (
            "result = {'type': 'string', 'value': 'Hello World'}"
        )
        mock_execute.side_effect = [
            Exception("Test error"),
            {"type": "string", "value": "Hello World"},
        ]

        smart_dataframe.head_df.to_csv = Mock(
            return_value="""country,gdp,happiness_index
China,654881226,6.66
Japan,9009692259,7.16
Spain,8446903488,6.38
"""
        )

        smart_datalake.chat("Hello world")

        last_prompt = smart_datalake.last_prompt
        if sys.platform.startswith("win"):
            last_prompt = last_prompt.replace("\r\n", "\n")

        assert (
            last_prompt
            == """<dataframe>
dfs[0]:10x3
country,gdp,happiness_index
China,654881226,6.66
Japan,9009692259,7.16
Spain,8446903488,6.38
</dataframe>

The user asked the following question:
Q: Hello world

You generated this python code:
result = {'type': 'string', 'value': 'Hello World'}

It fails with the following error:
Test error

Fix the python code above and return the new python code:"""  # noqa: E501
        )

    @patch("os.makedirs")
    def test_load_config_with_cache(self, mock_makedirs, smart_datalake):
        # Modify the smart_datalake's configuration
        smart_datalake.config.save_charts = True
        smart_datalake.config.enable_cache = True

        # Call the initialize method
        smart_datalake.load_config(smart_datalake.config)

        # Assertions for enabling cache
        cache_dir = os.path.join(os.getcwd(), "cache")
        mock_makedirs.assert_any_call(
            cache_dir, mode=DEFAULT_FILE_PERMISSIONS, exist_ok=True
        )

        # Assertions for saving charts
        charts_dir = os.path.join(os.getcwd(), smart_datalake.config.save_charts_path)
        mock_makedirs.assert_any_call(
            charts_dir, mode=DEFAULT_FILE_PERMISSIONS, exist_ok=True
        )

    @patch("os.makedirs")
    def test_load_config_without_cache(self, mock_makedirs, smart_datalake):
        # Modify the smart_datalake's configuration
        smart_datalake.config.save_charts = True
        smart_datalake.config.enable_cache = False

        # Call the initialize method
        smart_datalake.load_config(smart_datalake.config)

        # Assertions for saving charts
        charts_dir = os.path.join(os.getcwd(), smart_datalake.config.save_charts_path)
        mock_makedirs.assert_called_once_with(
            charts_dir, mode=DEFAULT_FILE_PERMISSIONS, exist_ok=True
        )

    def test_validate_true_direct_sql_with_non_connector(self, llm, sample_df):
        # raise exception with non connector
        SmartDatalake(
            [sample_df],
            config={"llm": llm, "enable_cache": False, "direct_sql": True},
        )

    def test_validate_direct_sql_with_connector(self, llm, sql_connector):
        # not exception is raised using single connector
        SmartDatalake(
            [sql_connector],
            config={"llm": llm, "enable_cache": False, "direct_sql": True},
        )

    def test_validate_false_direct_sql_with_connector(self, llm, sql_connector):
        # not exception is raised using single connector
        SmartDatalake(
            [sql_connector],
            config={"llm": llm, "enable_cache": False, "direct_sql": False},
        )

    def test_validate_false_direct_sql_with_two_different_connector(
        self, llm, sql_connector, pgsql_connector
    ):
        # not exception is raised using single connector
        SmartDatalake(
            [sql_connector, pgsql_connector],
            config={"llm": llm, "enable_cache": False, "direct_sql": False},
        )
