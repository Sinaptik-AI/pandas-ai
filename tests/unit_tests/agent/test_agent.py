import os
from typing import Optional
from unittest.mock import MagicMock, Mock, patch

import pandas as pd
import pytest

from pandasai.agent.base import Agent
from pandasai.config import Config, ConfigManager
from pandasai.dataframe.base import DataFrame
from pandasai.exceptions import CodeExecutionError
from pandasai.helpers.dataframe_serializer import DataframeSerializerType
from pandasai.llm.fake import FakeLLM


class TestAgent:
    "Unit tests for Agent class"

    @pytest.fixture
    def sample_df(self) -> DataFrame:
        return DataFrame(
            {
                "country": ["United States", "United Kingdom", "Japan", "China"],
                "gdp": [
                    19294482071552,
                    2891615567872,
                    4380756541440,
                    14631844184064,
                ],
                "happiness_index": [6.94, 7.22, 5.87, 5.12],
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

    @pytest.fixture(autouse=True)
    def mock_bamboo_llm(self):
        with patch("pandasai.llm.bamboo_llm.BambooLLM") as mock:
            mock.return_value = Mock(type="bamboo")
            yield mock

    def test_constructor(self, sample_df, config):
        agent_1 = Agent(sample_df, config)
        agent_2 = Agent([sample_df], config)

        # test multiple agents instances data overlap
        agent_1._state.memory.add("Which country has the highest gdp?", True)
        memory = agent_1._state.memory.all()
        assert len(memory) == 1

        memory = agent_2._state.memory.all()
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

    @patch("pandasai.agent.base.CodeGenerator")
    def test_code_generation(self, mock_generate_code, sample_df, config):
        # Create an Agent instance for testing
        mock_generate_code.generate_code.return_value = (
            "print(United States has the highest gdp)",
            [],
        )
        agent = Agent(sample_df, config)
        agent._code_generator = mock_generate_code

        # Test the chat function
        response, additional_dependencies = agent.generate_code(
            "Which country has the highest gdp?"
        )
        assert agent._code_generator.generate_code.called
        assert isinstance(response, str)
        assert isinstance(additional_dependencies, list)

        assert response == "print(United States has the highest gdp)"

    @patch("pandasai.agent.base.CodeGenerator")
    def test_generate_code_with_cache_hit(self, mock_generate_code, agent: Agent):
        # Set up the cache to return a pre-cached response
        cached_code = "print('Cached result: US has the highest GDP.')"
        agent._state.config.enable_cache = True
        agent._state.cache.get = MagicMock(return_value=cached_code)

        # Mock code generator is not used because of the cache hit
        mock_generate_code.validate_and_clean_code.return_value = (
            "print('Cached result: US has the highest GDP.')",
            [],
        )

        # Generate code
        response, _ = agent.generate_code("Which country has the highest GDP?")

        # Check that the cached code was used
        assert response == cached_code
        assert mock_generate_code.validate_and_clean_code.called_with(cached_code)

    @patch("pandasai.agent.base.CodeGenerator")
    def test_generate_code_with_cache_miss(self, mock_generate_code, agent: Agent):
        # Set up the cache to return no cached response
        agent._state.config.enable_cache = True
        agent._state.cache.get = MagicMock(return_value=None)

        # Mock the code generator to return a new response
        mock_generate_code.generate_code.return_value = (
            "print('New result: US has the highest GDP.')",
            [],
        )
        agent._code_generator = mock_generate_code

        # Generate code
        response, additional_dependencies = agent.generate_code(
            "Which country has the highest GDP?"
        )

        # Check that the cache miss triggered new code generation
        assert mock_generate_code.generate_code.called
        assert response == "print('New result: US has the highest GDP.')"

    @patch("pandasai.agent.base.CodeGenerator")
    def test_generate_code_with_direct_sql(self, mock_generate_code, agent: Agent):
        # Enable direct SQL in the config
        agent._state.config.direct_sql = True

        # Mock the code generator to return a SQL-based response
        mock_generate_code.generate_code.return_value = (
            "SELECT country FROM countries ORDER BY gdp DESC LIMIT 1;",
            [],
        )
        agent._code_generator = mock_generate_code

        # Generate code
        response, additional_dependencies = agent.generate_code(
            "Which country has the highest GDP?"
        )

        # Check that the SQL-specific prompt was used
        assert mock_generate_code.generate_code.called
        assert response == "SELECT country FROM countries ORDER BY gdp DESC LIMIT 1;"

    @patch("pandasai.agent.base.CodeGenerator")
    def test_generate_code_logs_generation(self, mock_generate_code, agent: Agent):
        # Mock the logger
        agent._state.logger.log = MagicMock()

        # Mock the code generator
        mock_generate_code.generate_code.return_value = (
            "print('Logging test.')",
            [],
        )
        agent._code_generator = mock_generate_code

        # Generate code
        response, additional_dependencies = agent.generate_code(
            "Test logging during code generation."
        )

        # Verify logger was called
        agent._state.logger.log.assert_any_call("Generating new code...")
        assert mock_generate_code.generate_code.called
        assert response == "print('Logging test.')"

    @patch("pandasai.agent.base.CodeGenerator")
    def test_generate_code_updates_last_prompt(self, mock_generate_code, agent: Agent):
        # Mock the code generator
        prompt = "Cust  om SQL prompt"
        mock_generate_code.generate_code.return_value = (
            "print('Prompt test.')",
            [],
        )
        agent._state.last_prompt_used = None
        agent._code_generator = mock_generate_code

        # Mock the prompt creation function
        with patch("pandasai.agent.base.get_chat_prompt", return_value=prompt):
            response, additional_dependencies = agent.generate_code(
                "Which country has the highest GDP?"
            )

        # Verify the last prompt used is updated
        assert agent._state.last_prompt_used == prompt
        assert mock_generate_code.generate_code.called
        assert response == "print('Prompt test.')"

    @patch("pandasai.agent.base.CodeExecutor")
    def test_execute_code_successful_execution(self, mock_code_executor, agent: Agent):
        # Mock CodeExecutor to return a successful result
        mock_code_executor.return_value.execute_and_return_result.return_value = {
            "result": "Execution successful"
        }
        mock_code_executor.return_value.add_to_env = MagicMock()

        # Execute the code
        code = "print('Hello, World!')"
        additional_dependencies = ["numpy"]
        result = agent.execute_code(code, additional_dependencies)

        # Verify the code was executed and the result is correct
        assert result == {"result": "Execution successful"}
        mock_code_executor.return_value.add_to_env.assert_any_call(
            "dfs", agent._state.dfs
        )
        mock_code_executor.return_value.execute_and_return_result.assert_called_with(
            code
        )

    @patch("pandasai.agent.base.CodeExecutor")
    def test_execute_code_with_direct_sql(self, mock_code_executor, agent: Agent):
        # Enable direct SQL in the config
        agent._state.config.direct_sql = True

        # Mock CodeExecutor to return a result
        mock_code_executor.return_value.execute_and_return_result.return_value = {
            "result": "SQL Execution successful"
        }
        mock_code_executor.return_value.add_to_env = MagicMock()

        # Mock SQL method in the DataFrame
        agent._state.dfs[0].execute_sql_query = MagicMock()

        # Execute the code
        code = "execute_sql_query('SELECT * FROM table')"
        additional_dependencies = []
        result = agent.execute_code(code, additional_dependencies)

        # Verify the SQL execution environment was set up correctly
        assert result == {"result": "SQL Execution successful"}
        mock_code_executor.return_value.add_to_env.assert_any_call(
            "execute_sql_query", agent._state.dfs[0].execute_sql_query
        )
        mock_code_executor.return_value.execute_and_return_result.assert_called_with(
            code
        )

    @patch("pandasai.agent.base.CodeExecutor")
    def test_execute_code_logs_execution(self, mock_code_executor, agent: Agent):
        # Mock the logger
        agent._state.logger.log = MagicMock()

        # Mock CodeExecutor to return a result
        mock_code_executor.return_value.execute_and_return_result.return_value = {
            "result": "Logging test successful"
        }

        # Execute the code
        code = "print('Logging test')"
        additional_dependencies = []
        result = agent.execute_code(code, additional_dependencies)

        # Verify the logger was called with the correct message
        agent._state.logger.log.assert_called_with(f"Executing code: {code}")
        assert result == {"result": "Logging test successful"}
        mock_code_executor.return_value.execute_and_return_result.assert_called_with(
            code
        )

    @patch("pandasai.agent.base.CodeExecutor")
    def test_execute_code_with_missing_dependencies(
        self, mock_code_executor, agent: Agent
    ):
        # Mock CodeExecutor to simulate a missing dependency error
        mock_code_executor.return_value.execute_and_return_result.side_effect = (
            ImportError("Missing dependency: pandas")
        )

        # Execute the code
        code = "import pandas as pd; print(pd.DataFrame())"
        additional_dependencies = ["pandas"]

        with pytest.raises(ImportError):
            agent.execute_code(code, additional_dependencies)

        # Verify the CodeExecutor was called despite the missing dependency
        mock_code_executor.return_value.execute_and_return_result.assert_called_with(
            code
        )

    @patch("pandasai.agent.base.CodeExecutor")
    def test_execute_code_handles_empty_code(self, mock_code_executor, agent: Agent):
        # Mock CodeExecutor to return an empty result
        mock_code_executor.return_value.execute_and_return_result.return_value = {}

        # Execute empty code
        code = ""
        additional_dependencies = []
        result = agent.execute_code(code, additional_dependencies)

        # Verify the result is empty and the code executor was not called
        assert result == {}
        mock_code_executor.return_value.execute_and_return_result.assert_called_with(
            code
        )

    def test_start_new_conversation(self, sample_df, config):
        agent = Agent(sample_df, config, memory_size=10)
        agent._state.memory.add("Which country has the highest gdp?", True)
        memory = agent._state.memory.all()
        assert len(memory) == 1
        agent.start_new_conversation()
        memory = agent._state.memory.all()
        assert len(memory) == 0

    def test_code_generation_success(self, agent: Agent):
        # Mock the code generator
        agent._code_generator = Mock()
        expected_code = "print('Test successful')"
        agent._code_generator.generate_code.return_value = (expected_code, [])

        code, deps = agent.generate_code("Test query")
        assert code == expected_code
        assert agent._code_generator.generate_code.call_count == 1

    def test_execute_with_retries_max_retries_exceeds(self, agent: Agent):
        # Mock execute_code to always raise an exception
        agent.execute_code = Mock()
        agent.execute_code.side_effect = CodeExecutionError("Test error")
        agent._regenerate_code_after_error = Mock()
        agent._regenerate_code_after_error.return_value = ("test_code", [])

        # Set max retries to 3 explicitly
        agent._state.config.max_retries = 3

        with pytest.raises(CodeExecutionError):
            agent.execute_with_retries("test_code", [])

        # Should be called max_retries times
        assert agent.execute_code.call_count == 4
        assert agent._regenerate_code_after_error.call_count == 3

    def test_execute_with_retries_success(self, agent: Agent):
        # Mock execute_code to fail twice then succeed
        agent.execute_code = Mock()
        expected_result = {
            "type": "string",
            "value": "Success",
        }  # Correct response format
        # Need enough side effects for all attempts including regenerated code
        agent.execute_code.side_effect = [
            CodeExecutionError("First error"),  # Original code fails
            CodeExecutionError("Second error"),  # First regenerated code fails
            CodeExecutionError("Third error"),  # Second regenerated code fails
            expected_result,  # Third regenerated code succeeds
        ]
        agent._regenerate_code_after_error = Mock()
        agent._regenerate_code_after_error.return_value = ("test_code", [])

        result = agent.execute_with_retries("test_code", [])
        # Response parser returns a String object with value accessible via .value
        assert result.value == "Success"
        # Should have 4 execute attempts and 3 regenerations
        assert agent.execute_code.call_count == 4
        assert agent._regenerate_code_after_error.call_count == 3

    def test_execute_with_retries_custom_retries(self, agent: Agent):
        # Test with custom number of retries
        agent._state.config.max_retries = 5
        agent.execute_code = Mock()
        agent.execute_code.side_effect = CodeExecutionError("Test error")
        agent._regenerate_code_after_error = Mock()
        agent._regenerate_code_after_error.return_value = ("test_code", [])

        with pytest.raises(CodeExecutionError):
            agent.execute_with_retries("test_code", [])

        # Should be called max_retries + 1 times (initial try + retries)
        assert agent.execute_code.call_count == 6
        assert agent._regenerate_code_after_error.call_count == 5

    def test_load_llm_with_pandasai_llm(self, agent: Agent, llm):
        assert agent._get_llm(llm) == llm

    def test_load_llm_none(self, agent: Agent, llm):
        mock_llm = FakeLLM()
        with patch("pandasai.agent.base.BambooLLM", return_value=mock_llm), patch.dict(
            os.environ, {"PANDASAI_API_KEY": "test_key"}
        ):
            config = agent._get_config({})
            assert isinstance(config, Config)
            assert config.llm == mock_llm

    def test_train_method_with_qa(self, agent):
        queries = ["query1", "query2"]
        codes = ["code1", "code2"]
        agent.train(queries, codes)

        agent._state.vectorstore.add_docs.assert_not_called()
        agent._state.vectorstore.add_question_answer.assert_called_once_with(
            queries, codes
        )

    def test_train_method_with_docs(self, agent):
        docs = ["doc1"]
        agent.train(docs=docs)

        agent._state.vectorstore.add_question_answer.assert_not_called()
        agent._state.vectorstore.add_docs.assert_called_once()
        agent._state.vectorstore.add_docs.assert_called_once_with(docs)

    def test_train_method_with_docs_and_qa(self, agent):
        docs = ["doc1"]
        queries = ["query1", "query2"]
        codes = ["code1", "code2"]
        agent.train(queries, codes, docs=docs)

        agent._state.vectorstore.add_question_answer.assert_called_once()
        agent._state.vectorstore.add_question_answer.assert_called_once_with(
            queries, codes
        )
        agent._state.vectorstore.add_docs.assert_called_once()
        agent._state.vectorstore.add_docs.assert_called_once_with(docs)

    def test_train_method_with_queries_but_no_code(self, agent):
        queries = ["query1", "query2"]
        with pytest.raises(ValueError):
            agent.train(queries)

    def test_train_method_with_code_but_no_queries(self, agent):
        codes = ["code1", "code2"]
        with pytest.raises(ValueError):
            agent.train(codes)

    def test_get_config_none(self, agent: Agent):
        """Test that _get_config returns global config when input is None"""
        mock_config = Config()
        with patch.object(ConfigManager, "get", return_value=mock_config):
            config = agent._get_config(None)
            assert config == mock_config

    def test_get_config_dict(self, agent: Agent):
        """Test that _get_config properly handles dict input"""
        mock_llm = FakeLLM()
        test_dict = {"save_logs": False, "verbose": True, "llm": mock_llm}
        config = agent._get_config(test_dict)
        assert isinstance(config, Config)
        assert config.save_logs is False
        assert config.verbose is True
        assert config.llm == mock_llm

    def test_get_config_dict_with_api_key(self, agent: Agent):
        """Test that _get_config adds BambooLLM when API key is present"""
        mock_llm = FakeLLM()
        with patch.dict(os.environ, {"PANDASAI_API_KEY": "test_key"}), patch(
            "pandasai.agent.base.BambooLLM", return_value=mock_llm
        ):
            config = agent._get_config({})
            assert isinstance(config, Config)
            assert config.llm == mock_llm

    def test_get_config_config(self, agent: Agent):
        """Test that _get_config returns Config object unchanged"""
        original_config = Config(save_logs=False, verbose=True)
        config = agent._get_config(original_config)
        assert config == original_config
        assert isinstance(config, Config)
