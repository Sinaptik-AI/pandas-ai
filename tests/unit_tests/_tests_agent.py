from typing import Optional
from unittest.mock import Mock

import pandas as pd
import pytest

from pandasai.agent import Agent
from pandasai.llm.fake import FakeLLM
from pandasai.prompts.explain_prompt import ExplainPrompt
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
    def llm(self, output: Optional[str] = None) -> FakeLLM:
        return FakeLLM(output=output)

    @pytest.fixture
    def config(self, llm: FakeLLM) -> dict:
        return {"llm": llm}

    @pytest.fixture
    def agent(self, sample_df: pd.DataFrame, config: dict) -> Agent:
        return Agent(sample_df, config)

    def test_constructor(self, sample_df, config):
        agent_1 = Agent(sample_df, config)
        assert isinstance(agent_1._lake, SmartDatalake)

        agent_2 = Agent([sample_df], config)
        assert isinstance(agent_2._lake, SmartDatalake)

        # test multiple agents instances data overlap
        agent_1._lake._memory.add("Which country has the highest gdp?", True)
        memory = agent_1._lake._memory.all()
        assert len(memory) == 1

        memory = agent_2._lake._memory.all()
        assert len(memory) == 0

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

    def test_start_new_conversation(self, sample_df, config):
        agent = Agent(sample_df, config, memory_size=10)
        agent._lake._memory.add("Which country has the highest gdp?", True)
        memory = agent._lake._memory.all()
        assert len(memory) == 1
        agent.start_new_conversation()
        memory = agent._lake._memory.all()
        assert len(memory) == 0

    def test_explain(self, agent: Agent):
        agent._lake.llm.call = Mock()
        clarification_response = """
Combine the Data: To find out who gets paid the most, 
I needed to match the names of people with the amounts of money they earn. 
It's like making sure the right names are next to the right amounts. 
I used a method to do this, like connecting pieces of a puzzle.
Find the Top Earner: After combining the data, I looked through it to find 
the person with the most money. 
It's like finding the person who has the most marbles in a game
        """
        agent._lake.llm.call.return_value = clarification_response

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
        agent._lake.llm.call = Mock()
        clarification_response = """
What is expected Salary Increase?
        """
        agent._lake.llm.call.return_value = clarification_response
        prompt = ExplainPrompt(
            conversation="test conversation",
            code="test code",
        )
        agent._call_llm_with_prompt(prompt)
        assert agent._lake.llm.call.call_count == 1

    def test_call_prompt_max_retries_exceeds(self, agent: Agent):
        # raises exception every time
        agent._lake.llm.call = Mock()
        agent._lake.llm.call.side_effect = Exception("Raise an exception")
        with pytest.raises(Exception):
            agent._call_llm_with_prompt("Test Prompt")

        assert agent._lake.llm.call.call_count == 3

    def test_call_prompt_max_retry_on_error(self, agent: Agent):
        # test the LLM call failed twice but succeed third time
        agent._lake.llm.call = Mock()
        agent._lake.llm.call.side_effect = [Exception(), Exception(), "LLM Result"]
        prompt = ExplainPrompt(conversation="test conversation", code="")
        result = agent._call_llm_with_prompt(prompt)
        assert result == "LLM Result"
        assert agent._lake.llm.call.call_count == 3

    def test_call_prompt_max_retry_twice(self, agent: Agent):
        # test the LLM call failed once but succeed second time
        agent._lake.llm.call = Mock()
        agent._lake.llm.call.side_effect = [Exception(), "LLM Result"]
        prompt = ExplainPrompt(conversation="test conversation", code="")
        result = agent._call_llm_with_prompt(prompt)

        assert result == "LLM Result"
        assert agent._lake.llm.call.call_count == 2

    def test_call_llm_with_prompt_no_retry_on_error(self, agent: Agent):
        # Test when LLM call raises an exception but retries are disabled

        agent._lake.config.use_error_correction_framework = False
        agent._lake.llm.call = Mock()
        agent._lake.llm.call.side_effect = Exception()
        with pytest.raises(Exception):
            agent._call_llm_with_prompt("Test Prompt")

        assert agent._lake.llm.call.call_count == 1

    def test_call_llm_with_prompt_max_retries_check(self, agent: Agent):
        # Test when LLM call raises an exception, but called call function
        #  'max_retries' time

        agent._lake.config.max_retries = 5
        agent._lake.llm.call = Mock()
        agent._lake.llm.call.side_effect = Exception()

        with pytest.raises(Exception):
            agent._call_llm_with_prompt("Test Prompt")

        assert agent._lake.llm.call.call_count == 5

    def test_rephrase(self, sample_df, config):
        agent = Agent(sample_df, config, memory_size=10)
        agent._lake.llm.call = Mock()
        clarification_response = """
How much has the total salary expense increased?
        """
        agent._lake.llm.call.return_value = clarification_response

        response = agent.rephrase_query("how much has the revenue increased?")

        assert response == (
            """
How much has the total salary expense increased?
        """
        )
