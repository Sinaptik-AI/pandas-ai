from typing import Optional
from unittest.mock import patch

import pandas as pd
import pytest

from pandasai.connectors.sql import (
    PostgreSQLConnector,
    SQLConnector,
    SQLConnectorConfig,
)
from pandasai.ee.agents.semantic_agent.pipeline.llm_call import LLMCall
from pandasai.helpers.logger import Logger
from pandasai.llm.bamboo_llm import BambooLLM
from pandasai.llm.fake import FakeLLM
from pandasai.pipelines.pipeline_context import PipelineContext
from tests.unit_tests.ee.helpers.schema import VIZ_QUERY_SCHEMA_STR


class MockBambooLLM(BambooLLM):
    def __init__(self):
        pass

    def call(self, *args, **kwargs):
        return VIZ_QUERY_SCHEMA_STR


class TestSemanticLLMCall:
    "Unit test for Validate Pipeline Input"

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
            dialect="pgsql",
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
    def config(self, llm):
        return {"llm": llm, "enable_cache": True}

    @pytest.fixture
    def context(self, sample_df, config):
        return PipelineContext([sample_df], config)

    @pytest.fixture
    def logger(self):
        return Logger(True, False)

    def test_init(self, context, config):
        # Test the initialization of the CodeGenerator
        code_generator = LLMCall()
        assert isinstance(code_generator, LLMCall)

    def test_validate_input_llm_call(self, sample_df, context, logger):
        input_validator = LLMCall()

        llm = MockBambooLLM()

        # context for true config
        config = {"llm": llm, "enable_cache": True, "direct_sql": False}

        context = PipelineContext([sample_df], config)

        input_validator.execute(input="test", context=context, logger=logger)

    def test_validate_input_with_direct_sql_false_and_non_connector(
        self, sample_df, logger
    ):
        input_validator = LLMCall()

        llm = MockBambooLLM()

        # context for true config
        config = {"llm": llm, "enable_cache": True, "direct_sql": False}

        context = PipelineContext([sample_df], config)

        result = input_validator.execute(input="test", context=context, logger=logger)

        assert result.output == [
            {
                "name": "Orders",
                "table": "orders",
                "measures": [
                    {"name": "order_count", "type": "count"},
                    {"name": "total_freight", "type": "sum", "sql": "freight"},
                ],
                "dimensions": [
                    {"name": "order_id", "type": "int", "sql": "order_id"},
                    {"name": "customer_id", "type": "string", "sql": "customer_id"},
                    {"name": "employee_id", "type": "int", "sql": "employee_id"},
                    {"name": "order_date", "type": "date", "sql": "order_date"},
                    {"name": "required_date", "type": "date", "sql": "required_date"},
                    {"name": "shipped_date", "type": "date", "sql": "shipped_date"},
                    {"name": "ship_via", "type": "int", "sql": "ship_via"},
                    {"name": "ship_name", "type": "string", "sql": "ship_name"},
                    {"name": "ship_address", "type": "string", "sql": "ship_address"},
                    {"name": "ship_city", "type": "string", "sql": "ship_city"},
                    {"name": "ship_region", "type": "string", "sql": "ship_region"},
                    {
                        "name": "ship_postal_code",
                        "type": "string",
                        "sql": "ship_postal_code",
                    },
                    {"name": "ship_country", "type": "string", "sql": "ship_country"},
                ],
                "joins": [],
            }
        ]

    def test_validate_input_llm_call_raise_exception(self, sample_df, context, logger):
        input_validator = LLMCall()

        class MockBambooLLM(BambooLLM):
            def __init__(self):
                pass

            def call(self, *args, **kwargs):
                return "Hello World!"

        llm = MockBambooLLM()

        # context for true config
        config = {"llm": llm, "enable_cache": True, "direct_sql": False}

        context = PipelineContext([sample_df], config)

        with pytest.raises(Exception):
            input_validator.execute(input="test", context=context, logger=logger)
