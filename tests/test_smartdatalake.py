"""Unit tests for the SmartDatalake class"""
import os
import sys

from typing import Optional
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from pandasai import SmartDataframe, SmartDatalake
from pandasai.connectors.base import SQLConnectorConfig
from pandasai.connectors.sql import PostgreSQLConnector, SQLConnector
from pandasai.exceptions import InvalidConfigError
from pandasai.helpers.code_manager import CodeManager
from pandasai.llm.fake import FakeLLM
from pandasai.constants import DEFAULT_FILE_PERMISSIONS

from langchain import OpenAI

from pandasai.prompts.direct_sql_prompt import DirectSQLPrompt
from pandasai.prompts.generate_python_code import GeneratePythonCodePrompt


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
        smart_datalake._llm = None
        assert smart_datalake._llm is None

        smart_datalake._load_llm(llm)
        assert smart_datalake._llm == llm

    def test_load_llm_with_langchain_llm(self, smart_datalake: SmartDatalake, llm):
        langchain_llm = OpenAI(openai_api_key="fake_key")

        smart_datalake._llm = None
        assert smart_datalake._llm is None

        smart_datalake._load_llm(langchain_llm)
        assert smart_datalake._llm._langchain_llm == langchain_llm

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

    def test_retry_on_error_with_single_df(
        self, smart_datalake: SmartDatalake, smart_dataframe: SmartDataframe
    ):
        code = """result = 'Hello World'"""

        smart_dataframe._get_sample_head = Mock(
            return_value=pd.DataFrame(
                {
                    "country": ["China", "Japan", "Spain"],
                    "gdp": [654881226, 9009692259, 8446903488],
                    "happiness_index": [6.66, 7.16, 6.38],
                }
            )
        )

        smart_datalake._retry_run_code(
            code=code,
            e=Exception("Test error"),
        )

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


You generated this python code:
result = 'Hello World'

It fails with the following error:
Test error

Fix the python code above and return the new python code:"""  # noqa: E501
        )

    @patch("os.makedirs")
    def test_initialize_with_cache(self, mock_makedirs, smart_datalake):
        # Modify the smart_datalake's configuration
        smart_datalake.config.save_charts = True
        smart_datalake.config.enable_cache = True

        # Call the initialize method
        smart_datalake.initialize()

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
    def test_initialize_without_cache(self, mock_makedirs, smart_datalake):
        # Modify the smart_datalake's configuration
        smart_datalake.config.save_charts = True
        smart_datalake.config.enable_cache = False

        # Call the initialize method
        smart_datalake.initialize()

        # Assertions for saving charts
        charts_dir = os.path.join(os.getcwd(), smart_datalake.config.save_charts_path)
        mock_makedirs.assert_called_once_with(
            charts_dir, mode=DEFAULT_FILE_PERMISSIONS, exist_ok=True
        )

    def test_get_chat_prompt(self, smart_datalake: SmartDatalake):
        # Test case 1: direct_sql is True
        smart_datalake._config.direct_sql = True
        gen_key, gen_prompt = smart_datalake._get_chat_prompt()
        expected_key = "direct_sql_prompt"
        assert gen_key == expected_key
        assert isinstance(gen_prompt, DirectSQLPrompt)

        # Test case 2: direct_sql is False
        smart_datalake._config.direct_sql = False
        gen_key, gen_prompt = smart_datalake._get_chat_prompt()
        expected_key = "generate_python_code"
        assert gen_key == expected_key
        assert isinstance(gen_prompt, GeneratePythonCodePrompt)

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

    def test_validate_true_direct_sql_with_two_different_connector(
        self, llm, sql_connector, pgsql_connector
    ):
        # not exception is raised using single connector
        # raise exception when two different connector
        with pytest.raises(InvalidConfigError):
            SmartDatalake(
                [sql_connector, pgsql_connector],
                config={"llm": llm, "enable_cache": False, "direct_sql": True},
            )
