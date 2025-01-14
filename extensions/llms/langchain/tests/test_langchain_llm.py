"""Unit tests for the base LLM class"""

import pytest
from langchain_community.chat_models import ChatOpenAI
from langchain_community.llms import OpenAI
from langchain_core.messages import AIMessage
from langchain_core.outputs import (
    ChatGeneration,
    GenerationChunk,
    LLMResult,
)
from pandasai_langchain.langchain import LangchainLLM

from pandasai.core.prompts.base import BasePrompt
from pandasai.llm.base import LLM


class TestLangchainLLM:
    """Unit tests for the LangChain wrapper LLM class"""

    @pytest.fixture
    def langchain_llm(self):
        class FakeOpenAI(OpenAI):
            openai_api_key = "fake_key"

            def generate(self, prompts, stop=None, run_manager=None, **kwargs):
                generation = GenerationChunk(text="Custom response")
                return LLMResult(generations=[[generation]])

        return FakeOpenAI()

    @pytest.fixture
    def langchain_chat_llm(self):
        class FakeChatOpenAI(ChatOpenAI):
            openai_api_key: str = "fake_key"

            def generate(self, prompts, stop=None, run_manager=None, **kwargs):
                generation = ChatGeneration(
                    message=AIMessage(content="Custom response")
                )
                return LLMResult(generations=[[generation]])

        return FakeChatOpenAI()

    @pytest.fixture
    def prompt(self):
        class MockBasePrompt(BasePrompt):
            template: str = "Hello"

        return MockBasePrompt()

    def test_langchain_llm_type(self, langchain_llm):
        langchain_wrapper = LangchainLLM(langchain_llm)

        assert langchain_wrapper.type == "langchain_openai"

    def test_langchain_model_call(self, langchain_llm, prompt):
        langchain_wrapper = LangchainLLM(langchain_llm)

        assert (
            langchain_wrapper.call(instruction=prompt, suffix="!") == "Custom response"
        )

    def test_langchain_chat_call(self, langchain_chat_llm, prompt):
        langchain_wrapper = LangchainLLM(langchain_chat_llm)

        assert (
            langchain_wrapper.call(instruction=prompt, suffix="!") == "Custom response"
        )

    def test_agent_integration(self):
        from unittest.mock import MagicMock, PropertyMock

        from pandasai.agent import Agent

        class FakeChatOpenAI(LLM):
            openai_api_key: str = "fake_key"

            @property
            def type(self) -> str:
                return "langchain_openai"

            def call(self, prompts, stop=None, run_manager=None, **kwargs):
                generation = ChatGeneration(
                    message=AIMessage(content="Custom response")
                )
                return LLMResult(generations=[[generation]])

        mock_langchain_llm = FakeChatOpenAI()
        type_property = PropertyMock(return_value="openai")
        type(mock_langchain_llm)._llm_type = type_property
        mock_langchain_llm.openai_api_key = "fake_key"
        mock_langchain_llm.call = lambda instruction, suffix: "Custom response"

        agent = Agent(
            dfs=[MagicMock()],
            config={"llm": mock_langchain_llm},
            vectorstore=MagicMock(),
        )
        print(agent._state.config.llm.type)
        assert agent._state.config.llm.type == "langchain_openai"
