"""Unit tests for LocalLLM"""

from unittest.mock import MagicMock, patch

import pytest

from pandasai.llm.local_llm import LocalLLM


@pytest.fixture
def mock_openai():
    with patch("pandasai.llm.local_llm.OpenAI") as mock_cls:
        mock_completions = MagicMock()
        mock_cls.return_value.chat.completions = mock_completions
        yield mock_completions


class TestLocalLLM:
    def test_type(self, mock_openai):
        llm = LocalLLM(api_base="http://localhost:11434/v1", model="codellama")
        assert llm.type == "local"

    def test_default_dummy_api_key(self, mock_openai):
        with patch("pandasai.llm.local_llm.OpenAI") as mock_cls:
            mock_cls.return_value.chat.completions = MagicMock()
            LocalLLM(api_base="http://localhost:11434/v1", model="codellama")
            _, kwargs = mock_cls.call_args
            assert kwargs["api_key"] == "dummy"

    def test_custom_api_key(self, mock_openai):
        with patch("pandasai.llm.local_llm.OpenAI") as mock_cls:
            mock_cls.return_value.chat.completions = MagicMock()
            LocalLLM(
                api_base="http://localhost:11434/v1",
                model="codellama",
                api_key="mykey",
            )
            _, kwargs = mock_cls.call_args
            assert kwargs["api_key"] == "mykey"

    def test_call_returns_content(self, mock_openai):
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "result code"
        mock_openai.create.return_value = mock_response

        llm = LocalLLM(api_base="http://localhost:11434/v1", model="codellama")

        instruction = MagicMock()
        instruction.to_string.return_value = "some prompt"

        result = llm.call(instruction)
        assert result == "result code"

    def test_call_passes_extra_params(self, mock_openai):
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "ok"
        mock_openai.create.return_value = mock_response

        llm = LocalLLM(
            api_base="http://localhost:11434/v1",
            model="codellama",
            temperature=0.5,
        )
        instruction = MagicMock()
        instruction.to_string.return_value = "prompt"
        llm.call(instruction)

        _, kwargs = mock_openai.create.call_args
        assert kwargs.get("temperature") == 0.5
