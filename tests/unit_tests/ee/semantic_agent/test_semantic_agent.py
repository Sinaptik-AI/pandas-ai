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
from pandasai.ee.agents.semantic_agent import SemanticAgent
from pandasai.exceptions import InvalidTrainJson
from pandasai.helpers.dataframe_serializer import DataframeSerializerType
from pandasai.llm.bamboo_llm import BambooLLM
from pandasai.llm.fake import FakeLLM
from tests.unit_tests.ee.helpers.schema import (
    VIZ_QUERY_SCHEMA,
    VIZ_QUERY_SCHEMA_OBJ,
    VIZ_QUERY_SCHEMA_STR,
)


class MockBambooLLM(BambooLLM):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call = MagicMock(return_value=VIZ_QUERY_SCHEMA_STR)


class TestSemanticAgent:
    "Unit tests for Agent class"

    @pytest.fixture
    def sample_df(self):
        return pd.DataFrame(
            {
                "order_id": [
                    10248,
                    10249,
                    10250,
                    10251,
                    10252,
                    10253,
                    10254,
                    10255,
                    10256,
                    10257,
                ],
                "customer_id": [
                    "VINET",
                    "TOMSP",
                    "HANAR",
                    "VICTE",
                    "SUPRD",
                    "HANAR",
                    "CHOPS",
                    "RICSU",
                    "WELLI",
                    "HILAA",
                ],
                "employee_id": [5, 6, 4, 3, 4, 3, 4, 7, 3, 4],
                "order_date": pd.to_datetime(
                    [
                        "1996-07-04",
                        "1996-07-05",
                        "1996-07-08",
                        "1996-07-08",
                        "1996-07-09",
                        "1996-07-10",
                        "1996-07-11",
                        "1996-07-12",
                        "1996-07-15",
                        "1996-07-16",
                    ]
                ),
                "required_date": pd.to_datetime(
                    [
                        "1996-08-01",
                        "1996-08-16",
                        "1996-08-05",
                        "1996-08-05",
                        "1996-08-06",
                        "1996-08-07",
                        "1996-08-08",
                        "1996-08-09",
                        "1996-08-12",
                        "1996-08-13",
                    ]
                ),
                "shipped_date": pd.to_datetime(
                    [
                        "1996-07-16",
                        "1996-07-10",
                        "1996-07-12",
                        "1996-07-15",
                        "1996-07-11",
                        "1996-07-16",
                        "1996-07-23",
                        "1996-07-26",
                        "1996-07-17",
                        "1996-07-22",
                    ]
                ),
                "ship_via": [3, 1, 2, 1, 2, 2, 2, 3, 2, 1],
                "ship_name": [
                    "Vins et alcools Chevalier",
                    "Toms Spezialitäten",
                    "Hanari Carnes",
                    "Victuailles en stock",
                    "Suprêmes délices",
                    "Hanari Carnes",
                    "Chop-suey Chinese",
                    "Richter Supermarkt",
                    "Wellington Importadora",
                    "HILARION-Abastos",
                ],
                "ship_address": [
                    "59 rue de l'Abbaye",
                    "Luisenstr. 48",
                    "Rua do Paço, 67",
                    "2, rue du Commerce",
                    "Boulevard Tirou, 255",
                    "Rua do Paço, 67",
                    "Hauptstr. 31",
                    "Starenweg 5",
                    "Rua do Mercado, 12",
                    "Carrera 22 con Ave. Carlos Soublette #8-35",
                ],
                "ship_city": [
                    "Reims",
                    "Münster",
                    "Rio de Janeiro",
                    "Lyon",
                    "Charleroi",
                    "Rio de Janeiro",
                    "Bern",
                    "Genève",
                    "Resende",
                    "San Cristóbal",
                ],
                "ship_region": [
                    "CJ",
                    None,
                    "RJ",
                    "RH",
                    None,
                    "RJ",
                    None,
                    None,
                    "SP",
                    "Táchira",
                ],
                "ship_postal_code": [
                    "51100",
                    "44087",
                    "05454-876",
                    "69004",
                    "B-6000",
                    "05454-876",
                    "3012",
                    "1204",
                    "08737-363",
                    "5022",
                ],
                "ship_country": [
                    "France",
                    "Germany",
                    "Brazil",
                    "France",
                    "Belgium",
                    "Brazil",
                    "Switzerland",
                    "Switzerland",
                    "Brazil",
                    "Venezuela",
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
    def agent(self, sample_df: pd.DataFrame) -> Agent:
        llm = MockBambooLLM()
        config = {"llm": llm}
        return SemanticAgent(sample_df, config, vectorstore=MagicMock())

    def test_base_agent_contruct(self, sample_df):
        llm = MockBambooLLM()
        BaseAgent(sample_df, {"llm": llm}, vectorstore=MagicMock())

    def test_base_agent_log_id_implement(self, sample_df):
        llm = MockBambooLLM()
        agent = BaseAgent(sample_df, {"llm": llm}, vectorstore=MagicMock())
        with pytest.raises(Exception):
            agent.last_query_log_id

    def test_base_agent_log_id_register_agent(self, sample_df):
        llm = MockBambooLLM()
        llm.call = MagicMock(return_value=VIZ_QUERY_SCHEMA_STR)
        agent = SemanticAgent(
            sample_df, {"llm": llm, "enable_cache": False}, vectorstore=MagicMock()
        )
        try:
            agent.init_duckdb_instance()
        except Exception:
            pytest.fail("InvalidConfigError was raised unexpectedly.")

    def test_constructor_with_no_bamboo(self, llm, sample_df):
        with pytest.raises(Exception):
            SemanticAgent(
                sample_df, {"llm": llm, "enable_cache": False}, vectorstore=MagicMock()
            )

    def test_constructor(self, sample_df):
        llm = MockBambooLLM()
        llm.call = MagicMock(return_value=VIZ_QUERY_SCHEMA_STR)
        agent = SemanticAgent(
            sample_df, {"llm": llm, "enable_cache": False}, vectorstore=MagicMock()
        )
        assert agent._schema == VIZ_QUERY_SCHEMA

    def test_last_log_id(self, sample_df):
        llm = MockBambooLLM()
        llm.call = MagicMock(return_value=VIZ_QUERY_SCHEMA_STR)
        agent = SemanticAgent(sample_df, {"llm": llm}, vectorstore=MagicMock())
        assert agent.last_query_log_id is None

    def test_last_error(self, sample_df):
        llm = MockBambooLLM()
        llm.call = MagicMock(return_value=VIZ_QUERY_SCHEMA_STR)
        agent = SemanticAgent(sample_df, {"llm": llm}, vectorstore=MagicMock())
        assert agent.last_error is None

    def test_return_is_object(self, sample_df):
        llm = MockBambooLLM()
        llm.call = MagicMock(return_value=VIZ_QUERY_SCHEMA_OBJ)
        agent = SemanticAgent(
            sample_df, {"llm": llm, "enable_cache": False}, vectorstore=MagicMock()
        )
        assert agent.last_query_log_id is None

    @patch("pandasai.helpers.cache.Cache.get")
    def test_cache_of_schema(self, mock_cache_get, sample_df):
        mock_cache_get.return_value = VIZ_QUERY_SCHEMA_STR
        llm = MockBambooLLM()
        llm.call = MagicMock(return_value=VIZ_QUERY_SCHEMA_STR)

        agent = SemanticAgent(sample_df, {"llm": llm}, vectorstore=MagicMock())

        assert not llm.call.called
        assert agent._schema == VIZ_QUERY_SCHEMA

    def test_train_method_with_qa(self, agent):
        queries = ["query1"]
        jsons = ['{"name": "test"}']
        agent.train(queries=queries, jsons=jsons)

        agent._vectorstore.add_docs.assert_not_called()
        agent._vectorstore.add_question_answer.assert_called_once_with(queries, jsons)

    def test_train_method_with_docs(self, agent):
        docs = ["doc1"]
        agent.train(docs=docs)

        agent._vectorstore.add_question_answer.assert_not_called()
        agent._vectorstore.add_docs.assert_called_once()
        agent._vectorstore.add_docs.assert_called_once_with(docs)

    def test_train_method_with_docs_and_qa(self, agent):
        docs = ["doc1"]
        queries = ["query1"]
        jsons = ['{"name": "test"}']
        agent.train(queries, jsons, docs=docs)

        agent._vectorstore.add_question_answer.assert_called_once()
        agent._vectorstore.add_question_answer.assert_called_once_with(queries, jsons)
        agent._vectorstore.add_docs.assert_called_once()
        agent._vectorstore.add_docs.assert_called_once_with(docs)

    def test_train_method_with_queries_but_no_code(self, agent):
        queries = ["query1", "query2"]
        with pytest.raises(ValueError):
            agent.train(queries)

    def test_train_method_with_code_but_no_queries(self, agent):
        jsons = ["code1", "code2"]
        with pytest.raises(InvalidTrainJson):
            agent.train(jsons=jsons)
