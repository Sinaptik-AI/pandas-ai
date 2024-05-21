from typing import Optional
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from pandasai.agent import Agent
from pandasai.agent.base import BaseAgent
from pandasai.connectors.sql import (
    PostgreSQLConnector,
    SQLConnector,
    SQLConnectorConfig,
)
from pandasai.ee.agents.visualization_agent import VisualizationAgent
from pandasai.helpers.dataframe_serializer import DataframeSerializerType
from pandasai.llm.bamboo_llm import BambooLLM
from pandasai.llm.fake import FakeLLM
from tests.unit_tests.ee.helpers.schema import VIZ_QUERY_SCHEMA_STR


class MockBambooLLM(BambooLLM):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call = MagicMock(return_value=VIZ_QUERY_SCHEMA_STR)


class TestVizAgent:
    "Unit tests for Agent class"

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
    def llm(self, output: Optional[str] = None) -> FakeLLM:
        return FakeLLM(output=output)

    @pytest.fixture
    def config(self, llm: FakeLLM) -> dict:
        return {"llm": llm, "dataframe_serializer": DataframeSerializerType.CSV}

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
    def agent(self, sample_df: pd.DataFrame, config: dict) -> Agent:
        return VisualizationAgent(sample_df, config, vectorstore=MagicMock())

    def test_base_agent_contruct(self, sample_df):
        llm = MockBambooLLM()
        BaseAgent(sample_df, {"llm": llm}, vectorstore=MagicMock())

    def test_constructor(self, sample_df):
        llm = MockBambooLLM()
        agent = VisualizationAgent(sample_df, {"llm": llm}, vectorstore=MagicMock())
        assert agent._schema == VIZ_QUERY_SCHEMA_STR

    def test_last_log_id(self, sample_df):
        llm = MockBambooLLM()
        agent = VisualizationAgent(sample_df, {"llm": llm}, vectorstore=MagicMock())
        assert agent.last_query_log_id is None

    @patch("pandasai.helpers.cache.Cache.get")
    def test_cache_of_schema(self, mock_cache_get, sample_df):
        mock_cache_get.return_value = VIZ_QUERY_SCHEMA_STR
        llm = MockBambooLLM()
        llm.call = MagicMock(return_value=VIZ_QUERY_SCHEMA_STR)

        agent = VisualizationAgent(sample_df, {"llm": llm}, vectorstore=MagicMock())

        assert not llm.call.called
        assert agent._schema == VIZ_QUERY_SCHEMA_STR
