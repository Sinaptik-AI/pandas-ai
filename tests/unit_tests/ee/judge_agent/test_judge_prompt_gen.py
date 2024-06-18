import re
from typing import Optional
from unittest.mock import patch

import pandas as pd
import pytest

from pandasai.connectors.sql import (
    PostgreSQLConnector,
    SQLConnector,
    SQLConnectorConfig,
)
from pandasai.ee.agents.judge_agent.pipeline.judge_prompt_generation import (
    JudgePromptGeneration,
)
from pandasai.helpers.logger import Logger
from pandasai.llm.bamboo_llm import BambooLLM
from pandasai.llm.fake import FakeLLM
from pandasai.pipelines.judge.judge_pipeline_input import JudgePipelineInput
from pandasai.pipelines.pipeline_context import PipelineContext
from tests.unit_tests.ee.helpers.schema import VIZ_QUERY_SCHEMA, VIZ_QUERY_SCHEMA_STR


class MockBambooLLM(BambooLLM):
    def __init__(self):
        pass

    def call(self, *args, **kwargs):
        return VIZ_QUERY_SCHEMA_STR


class TestJudgePromptGeneration:
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
        code_generator = JudgePromptGeneration()
        assert isinstance(code_generator, JudgePromptGeneration)

    def test_validate_input_semantic_prompt(self, sample_df, context, logger):
        semantic_prompter = JudgePromptGeneration()

        llm = MockBambooLLM()

        # context for true config
        config = {"llm": llm, "enable_cache": True, "direct_sql": False}

        context = PipelineContext([sample_df], config)

        context.memory.add("hello word!", True)

        context.add("df_schema", VIZ_QUERY_SCHEMA)

        input_data = JudgePipelineInput(
            query="What is test?", code="print('Code Data')"
        )

        response = semantic_prompter.execute(
            input_data=input_data, context=context, logger=logger
        )

        match = re.search(
            r"Today is ([A-Za-z]+, [A-Za-z]+ \d{1,2}, \d{4} \d{2}:\d{2} [APM]{2})",
            response.output.to_string(),
        )
        datetime_str = match.group(1)

        assert (
            response.output.to_string()
            == f"""Today is {datetime_str}
### QUERY
What is test?
### GENERATED CODE
print('Code Data')

Reason step by step and at the end answer:
1. Explain what the code does
2. Explain what the user query asks for
3. Strictly compare the query with the code that is generated
Always return <Yes> or <No> if exactly meets the requirements"""
        )
