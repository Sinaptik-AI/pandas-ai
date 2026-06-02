"""Unit tests for the MiniMax LLM class"""

import os
from unittest import mock

import openai
import pytest

from extensions.llms.minimax.pandasai_minimax import MiniMax
from pandasai.core.prompts.base import BasePrompt
from pandasai.exceptions import APIKeyNotFoundError, UnsupportedModelError


class OpenAIObject:
    def __init__(self, dictionary):
        self.__dict__.update(dictionary)


class TestMiniMaxLLM:
    """Unit tests for the MiniMax LLM class"""

    @pytest.fixture
    def prompt(self):
        class MockBasePrompt(BasePrompt):
            template: str = "instruction"

        return MockBasePrompt()

    def test_type_without_token(self):
        with mock.patch.dict(os.environ, clear=True):
            with pytest.raises(APIKeyNotFoundError):
                MiniMax()

    def test_type_with_token(self):
        assert MiniMax(api_token="test").type == "minimax"

    def test_default_model(self):
        llm = MiniMax(api_token="test")
        assert llm.model == "MiniMax-M3"

    def test_default_api_base(self):
        llm = MiniMax(api_token="test")
        assert llm.api_base == "https://api.minimax.io/v1"

    def test_default_temperature(self):
        llm = MiniMax(api_token="test")
        assert llm.temperature == 0.1

    def test_proxy(self):
        proxy = "http://proxy.mycompany.com:8080"
        client = MiniMax(api_token="test", openai_proxy=proxy)
        assert client.openai_proxy == proxy
        assert openai.proxy["http"] == proxy
        assert openai.proxy["https"] == proxy

    def test_params_setting(self):
        llm = MiniMax(
            api_token="test",
            model="MiniMax-M2.7-highspeed",
            temperature=0.5,
            max_tokens=50,
            top_p=1.0,
            frequency_penalty=2.0,
            presence_penalty=3.0,
            stop=["\n"],
        )

        assert llm.model == "MiniMax-M2.7-highspeed"
        assert llm.temperature == 0.5
        assert llm.max_tokens == 50
        assert llm.top_p == 1.0
        assert llm.frequency_penalty == 2.0
        assert llm.presence_penalty == 3.0
        assert llm.stop == ["\n"]

    def test_completion(self, mocker):
        expected_text = "This is the generated text."
        expected_response = OpenAIObject(
            {
                "choices": [{"text": expected_text}],
                "usage": {
                    "prompt_tokens": 2,
                    "completion_tokens": 1,
                    "total_tokens": 3,
                },
                "model": "MiniMax-M3",
            }
        )

        minimax = MiniMax(api_token="test")
        mocker.patch.object(minimax, "chat_completion", return_value=expected_response)
        result = minimax.chat_completion("Some prompt.")

        minimax.chat_completion.assert_called_once_with("Some prompt.")
        assert result == expected_response

    def test_chat_completion(self, mocker):
        minimax = MiniMax(api_token="test")
        expected_response = OpenAIObject(
            {
                "choices": [
                    {
                        "text": "Hello, how can I help you today?",
                        "index": 0,
                        "logprobs": None,
                        "finish_reason": "stop",
                        "start_text": "",
                    }
                ]
            }
        )

        mocker.patch.object(
            minimax, "chat_completion", return_value=expected_response
        )

        result = minimax.chat_completion("Hi")
        minimax.chat_completion.assert_called_once_with("Hi")

        assert result == expected_response

    def test_call_with_unsupported_model(self, prompt):
        with pytest.raises(
            UnsupportedModelError,
        ):
            MiniMax(api_token="test", model="not-a-model")

    def test_call_m3_model(self, mocker, prompt):
        minimax = MiniMax(api_token="test", model="MiniMax-M3")
        mocker.patch.object(minimax, "chat_completion", return_value="response")

        result = minimax.call(instruction=prompt)
        assert result == "response"

    def test_call_m27_model(self, mocker, prompt):
        minimax = MiniMax(api_token="test", model="MiniMax-M2.7")
        mocker.patch.object(minimax, "chat_completion", return_value="response")

        result = minimax.call(instruction=prompt)
        assert result == "response"

    def test_call_m27_highspeed_model(self, mocker, prompt):
        minimax = MiniMax(api_token="test", model="MiniMax-M2.7-highspeed")
        mocker.patch.object(minimax, "chat_completion", return_value="response")

        result = minimax.call(instruction=prompt)
        assert result == "response"

    def test_is_chat_model(self):
        llm = MiniMax(api_token="test")
        assert llm._is_chat_model is True

    def test_env_api_key(self):
        with mock.patch.dict(os.environ, {"MINIMAX_API_KEY": "env-test-key"}):
            llm = MiniMax()
            assert llm.api_token == "env-test-key"

    def test_custom_api_base(self):
        llm = MiniMax(api_token="test", api_base="https://custom.api.com/v1")
        assert llm.api_base == "https://custom.api.com/v1"
