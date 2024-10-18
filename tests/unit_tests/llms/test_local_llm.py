"""Unit tests for the local LLM class"""

from unittest.mock import MagicMock, patch

import pytest

from pandasai.helpers.memory import Memory
from extensions.llms.local.pandasai_local.local_llm import LocalLLM
from pandasai.prompts import BasePrompt


@pytest.fixture
def client():
    with patch("pandasai.llm.local_llm.OpenAI") as client:
        mock_completions = MagicMock()
        mock_response = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Mocked response"))]
        )
        mock_completions.create.return_value = mock_response
        client.return_value.chat.completions = mock_completions
        yield client


@pytest.fixture
def local_llm(client):
    return LocalLLM(api_base="http://localhost:1234/v1", model="bamboo-llm")


@pytest.fixture
def prompt():
    class MockBasePrompt(BasePrompt):
        template: str = "Hello"

    return MockBasePrompt()


class TestLocalLLM:
    """Unit tests for the local LLM class"""

    def test_local_llm_type(self, local_llm):
        assert local_llm.type == "local"

    def test_api_key_not_empty(self, client):
        LocalLLM(api_base="http://localhost:1234/v1")

        client.assert_called_once()
        _, kwargs = client.call_args
        assert "api_key" in kwargs
        assert kwargs["api_key"] != ""

    def test_chat_completion_no_memory(self, local_llm, client):
        expected_text = "This is the generated text."
        mock_response = MagicMock(
            choices=[MagicMock(message=MagicMock(content=expected_text))]
        )
        mock_create = client.return_value.chat.completions.create
        mock_create.return_value = mock_response

        result = local_llm.chat_completion("Hello", None)
        assert result == expected_text
        mock_create.assert_called_once()

    def test_chat_completion_with_memory(self, local_llm, client):
        expected_text = "This is the generated text."
        memory = Memory()
        memory.add("Previous user message", True)
        memory.add("Previous assistant message", False)
        mock_response = MagicMock(
            choices=[MagicMock(message=MagicMock(content=expected_text))]
        )
        mock_create = client.return_value.chat.completions.create
        mock_create.return_value = mock_response

        result = local_llm.chat_completion("Hello", memory)
        assert result == expected_text
        mock_create.assert_called_once()

        _, kwargs = mock_create.call_args
        assert "messages" in kwargs
        assert len(kwargs["messages"]) == 3

    def test_call_method(self, local_llm, client, prompt):
        expected_text = "This is the generated text."
        mock_response = MagicMock(
            choices=[MagicMock(message=MagicMock(content=expected_text))]
        )
        mock_create = client.return_value.chat.completions.create
        mock_create.return_value = mock_response

        result = local_llm.call(instruction=prompt)
        assert result == expected_text
        mock_create.assert_called_once()
