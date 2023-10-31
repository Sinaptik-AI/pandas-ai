"""Unit tests for the openai LLM class"""
import openai
import pytest

from pandasai.exceptions import APIKeyNotFoundError, UnsupportedModelError
from pandasai.llm import OpenAI
from pandasai.prompts import AbstractPrompt
from openai.openai_object import OpenAIObject


class TestOpenAILLM:
    """Unit tests for the openai LLM class"""

    @pytest.fixture
    def prompt(self):
        class MockAbstractPrompt(AbstractPrompt):
            template: str = "instruction"

        return MockAbstractPrompt()

    def test_type_without_token(self):
        with pytest.raises(APIKeyNotFoundError):
            OpenAI().type

    def test_type_with_token(self):
        assert OpenAI(api_token="test").type == "openai"

    def test_type_with_key_path(self):
        assert OpenAI(api_key_path=".key").type == "openai"

    def test_proxy(self):
        proxy = "http://proxy.mycompany.com:8080"
        client = OpenAI(api_token="test", openai_proxy=proxy)
        assert client.openai_proxy == proxy
        assert openai.proxy["http"] == proxy
        assert openai.proxy["https"] == proxy

    def test_params_setting(self):
        llm = OpenAI(
            api_token="test",
            model="GPT-3",
            temperature=0.5,
            max_tokens=50,
            top_p=1.0,
            frequency_penalty=2.0,
            presence_penalty=3.0,
            stop=["\n"],
        )

        assert llm.model == "GPT-3"
        assert llm.temperature == 0.5
        assert llm.max_tokens == 50
        assert llm.top_p == 1.0
        assert llm.frequency_penalty == 2.0
        assert llm.presence_penalty == 3.0
        assert llm.stop == ["\n"]

    def test_completion(self, mocker):
        openai_mock = mocker.patch("openai.Completion.create")
        expected_text = "This is the generated text."
        openai_mock.return_value = OpenAIObject.construct_from(
            {
                "choices": [{"text": expected_text}],
                "usage": {
                    "prompt_tokens": 2,
                    "completion_tokens": 1,
                    "total_tokens": 3,
                },
                "model": "gpt-35-turbo",
            }
        )

        openai = OpenAI(api_token="test")
        result = openai.completion("Some prompt.")

        openai_mock.assert_called_once_with(
            model=openai.model,
            prompt="Some prompt.",
            temperature=openai.temperature,
            max_tokens=openai.max_tokens,
            top_p=openai.top_p,
            frequency_penalty=openai.frequency_penalty,
            presence_penalty=openai.presence_penalty,
        )

        assert result == expected_text

    def test_chat_completion(self, mocker):
        openai = OpenAI(api_token="test")
        expected_response = OpenAIObject.construct_from(
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

        mocker.patch.object(openai, "chat_completion", return_value=expected_response)

        result = openai.chat_completion("Hi")
        assert result == expected_response

    def test_call_with_unsupported_model(self, prompt):
        with pytest.raises(
            UnsupportedModelError,
            match=(
                "Unsupported model: The model 'not a model' doesn't exist "
                "or is not supported yet."
            ),
        ):
            llm = OpenAI(api_token="test", model="not a model")
            llm.call(instruction=prompt)

    def test_call_supported_completion_model(self, mocker, prompt):
        openai = OpenAI(api_token="test", model="gpt-3.5-turbo-instruct")
        mocker.patch.object(openai, "completion", return_value="response")

        result = openai.call(instruction=prompt)
        assert result == "response"

    def test_call_supported_chat_model(self, mocker, prompt):
        openai = OpenAI(api_token="test", model="gpt-4")
        mocker.patch.object(openai, "chat_completion", return_value="response")

        result = openai.call(instruction=prompt)
        assert result == "response"

    def test_call_finetuned_model(self, mocker, prompt):
        openai = OpenAI(api_token="test", model="ft:gpt-3.5-turbo:my-org:custom_suffix:id")
        mocker.patch.object(openai, "chat_completion", return_value="response")

        result = openai.call(instruction=prompt)
        assert result == "response"
