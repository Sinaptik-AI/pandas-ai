from typing import Optional
from unittest.mock import patch
import pandas as pd

import pytest
from pandasai.connectors.sql import (
    PostgreSQLConnector,
    SQLConnector,
    SQLConnectorConfig,
)
from pandasai.exceptions import InvalidConfigError
from pandasai.helpers.logger import Logger

from pandasai.llm.fake import FakeLLM
from pandasai.pipelines.pipeline_context import PipelineContext
from pandasai.pipelines.smart_datalake_chat.validate_pipeline_input import (
    ValidatePipelineInput,
)
from pandasai.pipelines.logic_unit_output import LogicUnitOutput

from pandasai.smart_dataframe import SmartDataframe


class TestValidatePipelineInput:
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
    def smart_dataframe(self, llm, sample_df):
        return SmartDataframe(sample_df, config={"llm": llm, "enable_cache": True})

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
        code_generator = ValidatePipelineInput()
        assert isinstance(code_generator, ValidatePipelineInput)

    def test_validate_input_with_direct_sql_false_and_non_connector(
        self, context, logger
    ):
        input_validator = ValidatePipelineInput()

        result = input_validator.execute(input="test", context=context, logger=logger)

        assert result.output == "test"

    def test_validate_input_with_direct_sql_true_and_non_connector(
        self, sample_df, llm, logger
    ):
        input_validator = ValidatePipelineInput()

        # context for true config
        config = {"llm": llm, "enable_cache": True, "direct_sql": True}

        context = PipelineContext([sample_df], config)
        with pytest.raises(InvalidConfigError):
            input_validator.execute(input="test", context=context, logger=logger)

    def test_validate_input_with_direct_sql_false_and_connector(
        self, sample_df, llm, logger, sql_connector
    ):
        input_validator = ValidatePipelineInput()

        # context for true config
        config = {"llm": llm, "enable_cache": True, "direct_sql": False}

        context = PipelineContext([sample_df, sql_connector], config)
        result = input_validator.execute(input="test", context=context, logger=logger)
        assert isinstance(result, LogicUnitOutput)
        assert result.output == "test"

    def test_validate_input_with_direct_sql_true_and_connector(
        self, sample_df, llm, logger, sql_connector
    ):
        input_validator = ValidatePipelineInput()

        # context for true config
        config = {"llm": llm, "enable_cache": True, "direct_sql": True}

        context = PipelineContext([sql_connector], config)
        result = input_validator.execute(input="test", context=context, logger=logger)
        assert isinstance(result, LogicUnitOutput)
        assert result.output == "test"

    def test_validate_input_with_direct_sql_true_and_connector_pandasdf(
        self, sample_df, llm, logger, sql_connector
    ):
        input_validator = ValidatePipelineInput()

        # context for true config
        config = {"llm": llm, "enable_cache": True, "direct_sql": True}

        context = PipelineContext([sample_df, sql_connector], config)
        with pytest.raises(InvalidConfigError):
            input_validator.execute(input="test", context=context, logger=logger)

    def test_validate_input_with_direct_sql_true_and_different_type_connector(
        self, pgsql_connector, llm, logger, sql_connector
    ):
        input_validator = ValidatePipelineInput()

        # context for true config
        config = {"llm": llm, "enable_cache": True, "direct_sql": True}

        context = PipelineContext([pgsql_connector, sql_connector], config)
        with pytest.raises(InvalidConfigError):
            input_validator.execute(input="test", context=context, logger=logger)
