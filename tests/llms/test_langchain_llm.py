"""Unit tests for the base LLM class"""

from langchain.llms import OpenAI
import pytest

from pandasai.llm import LangchainLLM
from pandasai.prompts import AbstractPrompt
from unittest.mock import Mock


class TestLangchainLLM:
    """Unit tests for the LangChain wrapper LLM class"""

    @pytest.fixture
    def langchain_llm(self):
        class FakeOpenAI(OpenAI):
            openai_api_key = "fake_key"

            def __call__(self, _prompt, stop=None, callbacks=None, **kwargs):
                return Mock(return_value="Custom response")()

        langchain_llm = FakeOpenAI()

        return langchain_llm

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
