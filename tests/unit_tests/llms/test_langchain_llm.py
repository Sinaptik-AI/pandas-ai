"""Unit tests for the base LLM class"""


import pytest
from langchain_core.messages import AIMessage
from langchain_core.outputs import (
    ChatGeneration,
    GenerationChunk,
    LLMResult,
)
from langchain_community.llms import OpenAI
from langchain_community.chat_models import ChatOpenAI

from pandasai.llm import LangchainLLM
from pandasai.prompts import AbstractPrompt


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
        class MockAbstractPrompt(AbstractPrompt):
            template: str = "Hello"

        return MockAbstractPrompt()

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
