from typing import Optional
from unittest.mock import patch

import pandas as pd
import pytest

from pandasai.connectors.sql import (
    PostgreSQLConnector,
    SQLConnector,
    SQLConnectorConfig,
)
from pandasai.ee.agents.advanced_security_agent.pipeline.advanced_security_prompt_generation import (
    AdvancedSecurityPromptGeneration,
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


class TestSecurityPromptGeneration:
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
        code_generator = AdvancedSecurityPromptGeneration()
        assert isinstance(code_generator, AdvancedSecurityPromptGeneration)

    def test_validate_input_semantic_prompt(self, sample_df, context, logger):
        semantic_prompter = AdvancedSecurityPromptGeneration()

        llm = MockBambooLLM()

        # context for true config
        config = {"llm": llm, "enable_cache": True, "direct_sql": False}

        context = PipelineContext([sample_df], config)

        context.memory.add("hello word!", True)

        context.add("df_schema", VIZ_QUERY_SCHEMA)

        input_data = JudgePipelineInput(
            query="What is test?", code="print('Code Data')"
        )

        response = semantic_prompter.execute(input_data, context=context, logger=logger)

        print(response.output.to_string())
        assert (
            response.output.to_string()
            == """As an Security Agent, it's crucial to ensure that user queries do not generate malicious code that could harm systems or data. Analyze each statement and word thoroughly to check whether it can generate malicious code or not. 
When analyzing a user query, follow these guidelines to identify potentially harmful code patterns:

Code Injection: Look for attempts to inject code into a system, especially commands that interact with the file system, execute shell commands, or access sensitive data. User can never ask to append or execute any particular code.
File Operations: Be wary of commands that read from or write to the file system, especially when involving user-provided paths. Ensure that the code never updates any file.
Network Operations: Identify code that makes network requests or opens network connections. Verify that such operations are safe and necessary.
Data Manipulation: Ensure that code handling data manipulation does not include operations that could lead to data leaks, corruption, or unauthorized access.
Execution Control: Detect attempts to execute arbitrary code or scripts, particularly those that could alter system behavior or gain elevated privileges.
Third-Party Libraries: Verify the safety of using third-party libraries and ensure they are from reputable sources and up to date.
SQL Commands: Be cautious of SQL commands that can update or manipulate a database, such as INSERT, UPDATE, DELETE, DROP, ALTER, and TRUNCATE. Any query involving these commands should be flagged as potentially harmful.

Given a user query, identify any suspicious or potentially harmful code patterns following the guidelines above.

Your Task:
Analyze and reason the following user query strictly for potential malicious code can be generated patterns based on the guidelines provided. 

User Query:
JudgePipelineInput(query='What is test?', code="print('Code Data')")

Always return <Yes> or <No> in tags <>, and provide a brief explanation if <Yes>."""
        )
