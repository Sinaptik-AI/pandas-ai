"""Unit tests for the openai LLM class"""
import openai
import pytest

from pandasai.exceptions import APIKeyNotFoundError, UnsupportedOpenAIModelError
from pandasai.llm import AzureOpenAI
from openai.openai_object import OpenAIObject


class TestAzureOpenAILLM:
    """Unit tests for the Azure Openai LLM class"""

    def test_type_without_token(self):
        with pytest.raises(APIKeyNotFoundError):
            AzureOpenAI()

    def test_type_without_endpoint(self):
        with pytest.raises(APIKeyNotFoundError):
            AzureOpenAI(api_token="test")

    def test_type_without_api_version(self):
        with pytest.raises(APIKeyNotFoundError):
            AzureOpenAI(api_token="test", api_base="test")

    def test_type_without_deployment(self):
        with pytest.raises(UnsupportedOpenAIModelError):
            AzureOpenAI(api_token="test", api_base="test", api_version="test")

    def test_type_with_token(self):
        assert (
            AzureOpenAI(
                api_token="test",
                api_base="test",
                api_version="test",
                deployment_name="test",
            ).type
            == "azure-openai"
        )

    def test_proxy(self):
        proxy = "http://proxy.mycompany.com:8080"
        client = AzureOpenAI(
            api_token="test",
            api_base="test",
            api_version="test",
            deployment_name="test",
            openai_proxy=proxy,
        )
        assert client.openai_proxy == proxy
        assert openai.proxy["http"] == proxy
        assert openai.proxy["https"] == proxy

    def test_params_setting(self):
        llm = AzureOpenAI(
            api_token="test",
            api_base="test",
            api_version="test",
            deployment_name="Deployed-GPT-3",
            is_chat_model=True,
            temperature=0.5,
            max_tokens=50,
            top_p=1.0,
            frequency_penalty=2.0,
            presence_penalty=3.0,
            stop=["\n"],
        )

        assert llm.engine == "Deployed-GPT-3"
        assert llm.is_chat_model
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

        openai = AzureOpenAI(
            api_token="test",
            api_base="test",
            api_version="test",
            deployment_name="test",
        )
        result = openai.completion("Some prompt.")

        openai_mock.assert_called_once_with(
            engine=openai.engine,
            prompt="Some prompt.",
            temperature=openai.temperature,
            max_tokens=openai.max_tokens,
            top_p=openai.top_p,
            frequency_penalty=openai.frequency_penalty,
            presence_penalty=openai.presence_penalty,
        )

        assert result == expected_text

    def test_chat_completion(self, mocker):
        openai = AzureOpenAI(
            api_token="test",
            api_base="test",
            api_version="test",
            deployment_name="test",
            is_chat_model=True,
        )
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
