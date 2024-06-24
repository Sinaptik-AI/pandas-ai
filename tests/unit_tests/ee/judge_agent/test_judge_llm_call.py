from typing import Optional
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from pandasai.connectors.sql import (
    PostgreSQLConnector,
    SQLConnector,
    SQLConnectorConfig,
)
from pandasai.ee.agents.judge_agent.pipeline.llm_call import LLMCall
from pandasai.exceptions import InvalidOutputValueMismatch
from pandasai.helpers.logger import Logger
from pandasai.llm.bamboo_llm import BambooLLM
from pandasai.llm.fake import FakeLLM
from pandasai.pipelines.logic_unit_output import LogicUnitOutput
from pandasai.pipelines.pipeline_context import PipelineContext
from tests.unit_tests.ee.helpers.schema import VIZ_QUERY_SCHEMA_STR


class MockBambooLLM(BambooLLM):
    def __init__(self):
        pass

    def call(self, *args, **kwargs):
        return VIZ_QUERY_SCHEMA_STR


class TestJudgeLLMCall:
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

    def test_llm_call(self, sample_df, context, logger, config):
        input_validator = LLMCall()

        config["llm"].call = MagicMock(return_value="<Yes>")

        context = PipelineContext([sample_df], config)

        result = input_validator.execute(input="test", context=context, logger=logger)

        assert isinstance(result, LogicUnitOutput)
        assert result.output is True

    def test_llm_call_no(self, sample_df, context, logger, config):
        input_validator = LLMCall()

        config["llm"].call = MagicMock(return_value="<No>")

        context = PipelineContext([sample_df], config)

        result = input_validator.execute(input="test", context=context, logger=logger)

        assert isinstance(result, LogicUnitOutput)
        assert result.output is False

    def test_llm_call_(self, sample_df, context, logger, config):
        input_validator = LLMCall()

        config["llm"].call = MagicMock(return_value="<No>")

        context = PipelineContext([sample_df], config)

        result = input_validator.execute(input="test", context=context, logger=logger)

        assert isinstance(result, LogicUnitOutput)
        assert result.output is False

    def test_llm_call_with_no_tags(self, sample_df, context, logger, config):
        input_validator = LLMCall()

        config["llm"].call = MagicMock(return_value="yes")

        context = PipelineContext([sample_df], config)

        with pytest.raises(InvalidOutputValueMismatch):
            input_validator.execute(input="test", context=context, logger=logger)
