import os
import sys
from typing import Optional
from unittest.mock import MagicMock, Mock, PropertyMock, patch

import pandas as pd
import pytest
from langchain import OpenAI

from pandasai.agent import Agent
from pandasai.connectors.sql import (
    PostgreSQLConnector,
    SQLConnector,
    SQLConnectorConfig,
)
from pandasai.constants import DEFAULT_FILE_PERMISSIONS
from pandasai.helpers.code_manager import CodeManager
from pandasai.helpers.dataframe_serializer import DataframeSerializerType
from pandasai.llm.fake import FakeLLM
from pandasai.llm.langchain import LangchainLLM
from pandasai.prompts.clarification_questions_prompt import ClarificationQuestionPrompt
from pandasai.prompts.explain_prompt import ExplainPrompt


class TestAgent:
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
    def agent(self, sample_df: pd.DataFrame, config: dict) -> Agent:
        return Agent(sample_df, config, vectorstore=MagicMock())

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

    def test_constructor(self, sample_df, config):
        agent_1 = Agent(sample_df, config)
        agent_2 = Agent([sample_df], config)

        # test multiple agents instances data overlap
        agent_1.context.memory.add("Which country has the highest gdp?", True)
        memory = agent_1.context.memory.all()
        assert len(memory) == 1

        memory = agent_2.context.memory.all()
        assert len(memory) == 0

    def test_chat(self, sample_df, config):
        # Create an Agent instance for testing
        agent = Agent(sample_df, config)
        agent.chat = Mock()
        agent.chat.return_value = "United States has the highest gdp"
        # Test the chat function
        response = agent.chat("Which country has the highest gdp?")
        assert agent.chat.called
        assert isinstance(response, str)
        assert response == "United States has the highest gdp"

    def test_code_generation(self, sample_df, config):
        # Create an Agent instance for testing
        agent = Agent(sample_df, config)
        agent.pipeline.code_generation_pipeline.run = Mock()
        agent.pipeline.code_generation_pipeline.run.return_value = (
            "print(United States has the highest gdp)"
        )
        # Test the chat function
        response = agent.generate_code("Which country has the highest gdp?")
        assert agent.pipeline.code_generation_pipeline.run.called
        assert isinstance(response, str)
        assert response == "print(United States has the highest gdp)"

    def test_code_generation_failure(self, sample_df, config):
        # Create an Agent instance for testing
        agent = Agent(sample_df, config)
        agent.pipeline.code_generation_pipeline.run = Mock()
        agent.pipeline.code_generation_pipeline.run.side_effect = Exception(
            "Raise an exception"
        )
        # Test the chat function
        response = agent.generate_code("Which country has the highest gdp?")
        assert agent.pipeline.code_generation_pipeline.run.called
        assert (
            response
            == "Unfortunately, I was not able to answer your question, because of the following error:\n\nRaise an exception\n"
        )

    def test_code_execution(self, sample_df, config):
        # Create an Agent instance for testing
        agent = Agent(sample_df, config)
        agent.pipeline.code_execution_pipeline.run = Mock()
        agent.pipeline.code_execution_pipeline.run.side_effect = Exception(
            "Raise an exception"
        )
        response = agent.execute_code("print(United States has the highest gdp)")
        assert agent.pipeline.code_execution_pipeline.run.called
        assert (
            response
            == "Unfortunately, I was not able to answer your question, because of the following error:\n\nRaise an exception\n"
        )

    def test_code_execution_failure(self, sample_df, config):
        # Create an Agent instance for testing
        agent = Agent(sample_df, config)
        agent.pipeline.code_execution_pipeline.run = Mock()
        agent.pipeline.code_execution_pipeline.run.return_value = (
            "United States has the highest gdp"
        )
        response = agent.execute_code("print(United States has the highest gdp)")
        assert agent.pipeline.code_execution_pipeline.run.called
        assert isinstance(response, str)
        assert response == "United States has the highest gdp"

    def test_start_new_conversation(self, sample_df, config):
        agent = Agent(sample_df, config, memory_size=10)
        agent.context.memory.add("Which country has the highest gdp?", True)
        memory = agent.context.memory.all()
        assert len(memory) == 1
        agent.start_new_conversation()
        memory = agent.context.memory.all()
        assert len(memory) == 0

    def test_clarification_questions(self, sample_df, config):
        agent = Agent(sample_df, config, memory_size=10)
        agent.context.config.llm.call = Mock()
        clarification_response = (
            '["What is happiest index for you?", "What is unit of measure for gdp?"]'
        )
        agent.context.config.llm.call.return_value = clarification_response

        questions = agent.clarification_questions("What is the happiest country?")
        assert len(questions) == 2
        assert questions[0] == "What is happiest index for you?"
        assert questions[1] == "What is unit of measure for gdp?"

    def test_clarification_questions_failure(self, sample_df, config):
        agent = Agent(sample_df, config, memory_size=10)
        agent.context.config.llm.call = Mock()

        agent.context.config.llm.call.return_value = Exception(
            "This is a mock exception"
        )

        with pytest.raises(Exception):
            agent.clarification_questions("What is the happiest country?")

    def test_clarification_questions_fail_non_json(self, sample_df, config):
        agent = Agent(sample_df, config, memory_size=10)
        agent.context.config.llm.call = Mock()

        agent.context.config.llm.call.return_value = "This is not json response"

        with pytest.raises(Exception):
            agent.clarification_questions("What is the happiest country?")

    def test_clarification_questions_max_3(self, sample_df, config):
        agent = Agent(sample_df, config, memory_size=10)
        agent.context.config.llm.call = Mock()
        clarification_response = (
            '["What is happiest index for you", '
            '"What is unit of measure for gdp", '
            '"How many countries are involved in the survey", '
            '"How do you want this data to be represented"]'
        )
        agent.context.config.llm.call.return_value = clarification_response

        questions = agent.clarification_questions("What is the happiest country?")

        assert isinstance(questions, list)
        assert len(questions) == 3

    def test_explain(self, agent: Agent):
        agent.context.config.llm.call = Mock()
        clarification_response = """
Combine the Data: To find out who gets paid the most, 
I needed to match the names of people with the amounts of money they earn. 
It's like making sure the right names are next to the right amounts. 
I used a method to do this, like connecting pieces of a puzzle.
Find the Top Earner: After combining the data, I looked through it to find 
the person with the most money. 
It's like finding the person who has the most marbles in a game
        """
        agent.context.config.llm.call.return_value = clarification_response

        response = agent.explain()

        assert response == (
            """
Combine the Data: To find out who gets paid the most, 
I needed to match the names of people with the amounts of money they earn. 
It's like making sure the right names are next to the right amounts. 
I used a method to do this, like connecting pieces of a puzzle.
Find the Top Earner: After combining the data, I looked through it to find 
the person with the most money. 
It's like finding the person who has the most marbles in a game
        """
        )

    def test_call_prompt_success(self, agent: Agent):
        agent.context.config.llm.call = Mock()
        clarification_response = """
What is expected Salary Increase?
        """
        agent.context.config.llm.call.return_value = clarification_response
        prompt = ExplainPrompt(
            context=agent.context,
            code="test code",
        )
        agent.call_llm_with_prompt(prompt)
        assert agent.context.config.llm.call.call_count == 1

    def test_call_prompt_max_retries_exceeds(self, agent: Agent):
        # raises exception every time
        agent.context.config.llm.call = Mock()
        agent.context.config.llm.call.side_effect = Exception("Raise an exception")
        with pytest.raises(Exception):
            agent.call_llm_with_prompt("Test Prompt")

        assert agent.context.config.llm.call.call_count == 3

    def test_call_prompt_max_retry_on_error(self, agent: Agent):
        # test the LLM call failed twice but succeed third time
        agent.context.config.llm.call = Mock()
        agent.context.config.llm.call.side_effect = [
            Exception(),
            Exception(),
            "LLM Result",
        ]
        prompt = ExplainPrompt(
            context=agent.context,
            code="test code",
        )
        result = agent.call_llm_with_prompt(prompt)
        assert result == "LLM Result"
        assert agent.context.config.llm.call.call_count == 3

    def test_call_prompt_max_retry_twice(self, agent: Agent):
        # test the LLM call failed once but succeed second time
        agent.context.config.llm.call = Mock()
        agent.context.config.llm.call.side_effect = [Exception(), "LLM Result"]
        prompt = ExplainPrompt(
            context=agent.context,
            code="test code",
        )
        result = agent.call_llm_with_prompt(prompt)

        assert result == "LLM Result"
        assert agent.context.config.llm.call.call_count == 2

    def test_call_llm_with_prompt_no_retry_on_error(self, agent: Agent):
        # Test when LLM call raises an exception but retries are disabled

        agent.context.config.use_error_correction_framework = False
        agent.context.config.llm.call = Mock()
        agent.context.config.llm.call.side_effect = Exception()
        with pytest.raises(Exception):
            agent.call_llm_with_prompt("Test Prompt")

        assert agent.context.config.llm.call.call_count == 1

    def test_call_llm_with_prompt_max_retries_check(self, agent: Agent):
        # Test when LLM call raises an exception, but called call function
        #  'max_retries' time

        agent.context.config.max_retries = 5
        agent.context.config.llm.call = Mock()
        agent.context.config.llm.call.side_effect = Exception()

        with pytest.raises(Exception):
            agent.call_llm_with_prompt("Test Prompt")

        assert agent.context.config.llm.call.call_count == 5

    def test_clarification_prompt_validate_output_false_case(self, agent: Agent):
        # Test whether the output is json or not
        agent.context.config.llm.call = Mock()
        agent.context.config.llm.call.return_value = "This is not json"

        prompt = ClarificationQuestionPrompt(
            context=agent.context,
            query="test query",
        )
        with pytest.raises(Exception):
            agent.call_llm_with_prompt(prompt)

    def test_clarification_prompt_validate_output_true_case(self, agent: Agent):
        # Test whether the output is json or not
        agent.context.config.llm.call = Mock()
        agent.context.config.llm.call.return_value = '["This is test question"]'

        prompt = ClarificationQuestionPrompt(
            context=agent.context,
            query="test query",
        )
        result = agent.call_llm_with_prompt(prompt)
        # Didn't raise any exception
        assert isinstance(result, str)

    def test_rephrase(self, sample_df, config):
        agent = Agent(sample_df, config, memory_size=10)
        agent.context.config.llm.call = Mock()
        clarification_response = """
How much has the total salary expense increased?
        """
        agent.context.config.llm.call.return_value = clarification_response

        response = agent.rephrase_query("how much has the revenue increased?")

        assert response == (
            """
How much has the total salary expense increased?
        """
        )

    def test_load_llm_with_pandasai_llm(self, agent: Agent, llm):
        assert agent.get_llm(llm) == llm

    def test_load_llm_with_langchain_llm(self, agent: Agent, llm):
        langchain_llm = OpenAI(openai_api_key="fake_key")

        config = agent.get_config({"llm": langchain_llm})
        assert isinstance(config.llm, LangchainLLM)
        assert config.llm.langchain_llm == langchain_llm

    @patch(
        "pandasai.pipelines.chat.code_execution.CodeManager.last_code_executed",
        new_callable=PropertyMock,
    )
    def test_last_code_executed(self, _mocked_property, agent: Agent):
        expected_code = "result = {'type': 'string', 'value': 'There are 10 countries in the dataframe.'}"
        _mocked_property.return_value = expected_code
        agent.chat("How many countries are in the dataframe?")
        assert agent.last_code_executed == expected_code

    @patch.object(
        CodeManager,
        "execute_code",
        return_value={
            "type": "string",
            "value": "There are 10 countries in the dataframe.",
        },
    )
    def test_last_result_is_saved(self, _mocked_method, agent: Agent):
        assert agent.last_result is None

        _mocked_method.__name__ = "execute_code"

        agent.chat("How many countries are in the dataframe?")
        assert agent.last_result == {
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
        self, mock_query_tracker_publish, _mocked_method, agent: Agent
    ):
        assert agent.last_result is None

        _mocked_method.__name__ = "execute_code"

        agent.chat("How many countries are in the dataframe?")
        mock_query_tracker_publish.assert_called()

    @patch(
        "pandasai.pipelines.chat.code_execution.CodeManager.execute_code",
        autospec=True,
    )
    @patch(
        "pandasai.pipelines.chat.code_generator.CodeGenerator.execute",
        autospec=True,
    )
    @patch(
        "pandasai.pipelines.chat.code_execution.traceback.format_exc",
        autospec=True,
    )
    def test_retry_on_error_with_single_df(
        self,
        mock_traceback,
        mock_generate,
        mock_execute,
        agent: Agent,
    ):
        mock_traceback.return_value = "Test error"
        mock_generate.return_value = (
            "result = {'type': 'string', 'value': 'Hello World'}"
        )
        mock_execute.side_effect = [
            Exception("Test error"),
            {"type": "string", "value": "Hello World"},
        ]

        agent.context.dfs[0].to_csv = Mock(
            return_value="""country,gdp,happiness_index
China,654881226,6.66
Japan,9009692259,7.16
Spain,8446903488,6.38
"""
        )

        agent.chat("Hello world")

        last_prompt = agent.last_prompt
        if sys.platform.startswith("win"):
            last_prompt = last_prompt.replace("\r\n", "\n")

        print(last_prompt)

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
### QUERY
 Hello world

You generated this python code:
result = {'type': 'string', 'value': 'Hello World'}

It fails with the following error:
Test error

Fix the python code above and return the new python code:"""  # noqa: E501
        )

    @patch("os.makedirs")
    def test_load_config_with_cache(self, mock_makedirs, agent):
        # Modify the agent's configuration
        agent.context.config.save_charts = True
        agent.context.config.enable_cache = True

        # Call the initialize method
        agent.configure()

        # Assertions for enabling cache
        cache_dir = os.path.join(os.getcwd(), "cache")
        mock_makedirs.assert_any_call(
            cache_dir, mode=DEFAULT_FILE_PERMISSIONS, exist_ok=True
        )

        # Assertions for saving charts
        charts_dir = os.path.join(os.getcwd(), agent.context.config.save_charts_path)
        mock_makedirs.assert_any_call(
            charts_dir, mode=DEFAULT_FILE_PERMISSIONS, exist_ok=True
        )

    @patch("os.makedirs")
    def test_load_config_without_cache(self, mock_makedirs, agent):
        # Modify the agent's configuration
        agent.context.config.save_charts = True
        agent.context.config.enable_cache = False

        # Call the initialize method
        agent.configure()

        # Assertions for saving charts
        charts_dir = os.path.join(os.getcwd(), agent.context.config.save_charts_path)
        mock_makedirs.assert_called_once_with(
            charts_dir, mode=DEFAULT_FILE_PERMISSIONS, exist_ok=True
        )

    def test_validate_true_direct_sql_with_non_connector(self, llm, sample_df):
        # raise exception with non connector
        Agent(
            [sample_df],
            config={"llm": llm, "enable_cache": False, "direct_sql": True},
        )

    def test_validate_direct_sql_with_connector(self, llm, sql_connector):
        # not exception is raised using single connector
        Agent(
            [sql_connector],
            config={"llm": llm, "enable_cache": False, "direct_sql": True},
        )

    def test_validate_false_direct_sql_with_connector(self, llm, sql_connector):
        # not exception is raised using single connector
        Agent(
            [sql_connector],
            config={"llm": llm, "enable_cache": False, "direct_sql": False},
        )

    def test_validate_false_direct_sql_with_two_different_connector(
        self, llm, sql_connector, pgsql_connector
    ):
        # not exception is raised using single connector
        Agent(
            [sql_connector, pgsql_connector],
            config={"llm": llm, "enable_cache": False, "direct_sql": False},
        )

    def test_train_method_with_qa(self, agent):
        queries = ["query1", "query2"]
        codes = ["code1", "code2"]
        agent.train(queries, codes)

        agent._vectorstore.add_docs.assert_not_called()
        agent._vectorstore.add_question_answer.assert_called_once_with(queries, codes)

    def test_train_method_with_docs(self, agent):
        docs = ["doc1"]
        agent.train(docs=docs)

        agent._vectorstore.add_question_answer.assert_not_called()
        agent._vectorstore.add_docs.assert_called_once()
        agent._vectorstore.add_docs.assert_called_once_with(docs)

    def test_train_method_with_docs_and_qa(self, agent):
        docs = ["doc1"]
        queries = ["query1", "query2"]
        codes = ["code1", "code2"]
        agent.train(queries, codes, docs=docs)

        agent._vectorstore.add_question_answer.assert_called_once()
        agent._vectorstore.add_question_answer.assert_called_once_with(queries, codes)
        agent._vectorstore.add_docs.assert_called_once()
        agent._vectorstore.add_docs.assert_called_once_with(docs)

    def test_train_method_with_queries_but_no_code(self, agent):
        queries = ["query1", "query2"]
        with pytest.raises(ValueError):
            agent.train(queries)

    def test_train_method_with_code_but_no_queries(self, agent):
        codes = ["code1", "code2"]
        with pytest.raises(ValueError):
            agent.train(codes)
