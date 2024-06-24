from typing import Optional
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from pandasai.agent import Agent
from pandasai.connectors.sql import (
    PostgreSQLConnector,
    SQLConnector,
    SQLConnectorConfig,
)
from pandasai.ee.agents.judge_agent import JudgeAgent
from pandasai.helpers.dataframe_serializer import DataframeSerializerType
from pandasai.llm.bamboo_llm import BambooLLM
from pandasai.llm.fake import FakeLLM
from tests.unit_tests.ee.helpers.schema import (
    VIZ_QUERY_SCHEMA_STR,
)


class MockBambooLLM(BambooLLM):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call = MagicMock(return_value=VIZ_QUERY_SCHEMA_STR)


class TestJudgeAgent:
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
    def agent(self) -> Agent:
        return JudgeAgent()

    def test_contruct_with_pipeline(self, sample_df):
        JudgeAgent(pipeline=MagicMock())
