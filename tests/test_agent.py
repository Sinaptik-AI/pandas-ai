from typing import Optional
from unittest.mock import Mock
from pandasai.agent import Agent
import pandas as pd
import pytest
from pandasai.llm.fake import FakeLLM

from pandasai.smart_datalake import SmartDatalake


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
    def llm(self, output: Optional[str] = None):
        return FakeLLM(output=output)

    @pytest.fixture
    def config(self, llm: FakeLLM):
        return {"llm": llm}

    def test_constructor(self, sample_df, config):
        agent = Agent(sample_df, config)
        assert isinstance(agent._lake, SmartDatalake)

        agent = Agent([sample_df], config)
        assert isinstance(agent._lake, SmartDatalake)

    def test_chat(self, sample_df, config):
        # Create an Agent instance for testing
        agent = Agent(sample_df, config)
        agent._lake.chat = Mock()
        agent._lake.chat.return_value = "United States has the highest gdp"
        # Test the chat function
        response = agent.chat("Which country has the highest gdp?")
        assert agent._lake.chat.called
        assert isinstance(response, str)
        assert response == "United States has the highest gdp"

    def test_chat_memory(self, sample_df, config):
        agent = Agent(sample_df, config, memory_size=10)
        agent._lake.chat = Mock()
        agent._lake.chat.return_value = "United States has the highest gdp"

        # Test the chat function
        agent.chat("Which country has the highest gdp?")

        memory = agent._memory.all()
        assert len(memory) == 2
        assert memory[0]["message"] == "Which country has the highest gdp?"
        assert memory[1]["message"] == "United States has the highest gdp"

        # Add another conversation
        agent._lake.chat.return_value = "United Kingdom has the second highest gdp"
        agent.chat("Which country has the second highest gdp?")

        memory = agent._memory.all()
        assert len(memory) == 4
        assert memory[0]["message"] == "Which country has the highest gdp?"
        assert memory[1]["message"] == "United States has the highest gdp"
        assert memory[2]["message"] == "Which country has the second highest gdp?"
        assert memory[3]["message"] == "United Kingdom has the second highest gdp"

    def test_chat_memory_rollup(self, sample_df, config):
        agent = Agent(sample_df, config, memory_size=1)
        agent._lake.chat = Mock()
        agent._lake.chat.return_value = "United States has the highest gdp"

        # Test the chat function
        agent.chat("Which country has the highest gdp?")

        memory = agent._memory.all()
        assert len(memory) == 2
        assert memory[0]["message"] == "Which country has the highest gdp?"
        assert memory[1]["message"] == "United States has the highest gdp"

        # Add another conversation
        agent._lake.chat.return_value = "United Kingdom has the second highest gdp"
        agent.chat("Which country has the second highest gdp?")

        memory = agent._memory.all()
        assert len(memory) == 2
        assert memory[0]["message"] == "Which country has the second highest gdp?"
        assert memory[1]["message"] == "United Kingdom has the second highest gdp"

    def test_chat_get_conversation(self, sample_df, config):
        agent = Agent(sample_df, config, memory_size=10)
        agent._lake.chat = Mock()
        agent._lake.chat.return_value = "United States has the highest gdp"

        agent.chat("Which country has the highest gdp?")

        conversation = agent._get_conversation()

        assert conversation == (
            "Question: Which country has the highest gdp?\n"
            "Answer: United States has the highest gdp"
        )

        # Add another conversation
        agent._lake.chat.return_value = "United Kingdom has the second highest gdp"
        agent.chat("Which country has the second highest gdp?")

        conversation = agent._get_conversation()
        assert conversation == (
            "Question: Which country has the highest gdp?\n"
            "Answer: United States has the highest gdp"
            "\nQuestion: Which country has the second highest gdp?\n"
            "Answer: United Kingdom has the second highest gdp"
        )

    def test_start_new_conversation(self, sample_df, config):
        agent = Agent(sample_df, config, memory_size=10)
        agent._lake.chat = Mock()
        agent._lake.chat.return_value = "United States has the highest gdp"

        agent.chat("Which country has the highest gdp?")

        memory = agent._memory.all()
        assert len(memory) == 2

        agent.start_new_conversation()
        memory = agent._memory.all()
        assert len(memory) == 0

        conversation = agent._get_conversation()
        assert conversation == ""

    def test_clarification_questions(self, sample_df, config):
        agent = Agent(sample_df, config, memory_size=10)
        agent._lake.llm.generate_code = Mock()
        clarification_response = (
            '["What is happiest index for you?", "What is unit of measure for gdp?"]'
        )
        agent._lake.llm.generate_code.return_value = clarification_response

        questions = agent.clarification_questions()
        assert len(questions) == 2
        assert questions[0] == "What is happiest index for you?"
        assert questions[1] == "What is unit of measure for gdp?"

    def test_clarification_questions_max_3(self, sample_df, config):
        agent = Agent(sample_df, config, memory_size=10)
        agent._lake.llm.generate_code = Mock()
        clarification_response = (
            '["What is happiest index for you", '
            '"What is unit of measure for gdp", '
            '"How many countries are involved in the survey", '
            '"How do you want this data to be represented"]'
        )
        agent._lake.llm.generate_code.return_value = clarification_response

        questions = agent.clarification_questions()
        assert len(questions) == 3
