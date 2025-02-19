"""Unit tests for the openai LLM class"""

import os
from unittest import mock

import openai
import pytest

from extensions.llms.openai.pandasai_openai import OpenAI, OpenAI_Reasoning
from pandasai.core.prompts.base import BasePrompt
from pandasai.exceptions import APIKeyNotFoundError, UnsupportedModelError


class OpenAIObject:
    def __init__(self, dictionary):
        self.__dict__.update(dictionary)


class TestOpenAILLM:
    """Unit tests for the openai LLM class"""

    @pytest.fixture
    def prompt(self):
        class MockBasePrompt(BasePrompt):
            template: str = "instruction"

        return MockBasePrompt()

    def test_type_without_token(self):
        with mock.patch.dict(os.environ, clear=True):
            with pytest.raises(APIKeyNotFoundError):
                OpenAI()

    def test_type_with_token(self):
        assert OpenAI(api_token="test").type == "openai"

    def test_proxy(self):
        proxy = "http://proxy.mycompany.com:8080"
        client = OpenAI(api_token="test", openai_proxy=proxy)
        assert client.openai_proxy == proxy
        assert openai.proxy["http"] == proxy
        assert openai.proxy["https"] == proxy

    def test_params_setting(self):
        llm = OpenAI(
            api_token="test",
            model="gpt-3.5-turbo",
            temperature=0.5,
            max_tokens=50,
            top_p=1.0,
            frequency_penalty=2.0,
            presence_penalty=3.0,
            stop=["\n"],
        )

        assert llm.model == "gpt-3.5-turbo"
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
                "model": "gpt-35-turbo",
            }
        )

        openai = OpenAI(api_token="test")
        mocker.patch.object(openai, "completion", return_value=expected_response)
        result = openai.completion("Some prompt.")

        openai.completion.assert_called_once_with("Some prompt.")
        assert result == expected_response

    def test_chat_completion(self, mocker):
        openai = OpenAI(api_token="test")
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

        mocker.patch.object(openai, "chat_completion", return_value=expected_response)

        result = openai.chat_completion("Hi")
        openai.chat_completion.assert_called_once_with("Hi")

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

    def test_call_with_system_prompt(self, mocker, prompt):
        openai = OpenAI(
            api_token="test", model="ft:gpt-3.5-turbo:my-org:custom_suffix:id"
        )
        mocker.patch.object(openai, "chat_completion", return_value="response")

        result = openai.call(instruction=prompt)
        assert result == "response"


class TestOpenAI_ReasoningLLM:
    """Unit tests for the Azure Openai LLM class"""

    def test_type_without_token(self):
        with pytest.raises(APIKeyNotFoundError):
            OpenAI_Reasoning()

    def test_type_without_endpoint(self):
        with pytest.raises(APIKeyNotFoundError):
            OpenAI_Reasoning(api_token="test")

    def test_type_without_api_version(self):
        with pytest.raises(APIKeyNotFoundError):
            OpenAI_Reasoning(api_token="test", azure_endpoint="test")

    def test_type_without_deployment(self):
        with pytest.raises(MissingModelError):
            OpenAI_Reasoning(api_token="test", azure_endpoint="test", api_version="test")

    def test_type_with_token(self):
        assert (
            OpenAI_Reasoning(
                api_token="test",
                azure_endpoint="test",
                api_version="test",
                deployment_name="test",
            ).type
            == "azure-openai"
        )

    def test_proxy(self):
        proxy = "http://proxy.mycompany.com:8080"
        client = OpenAI_Reasoning(
            api_token="test",
            azure_endpoint="test",
            api_version="test",
            deployment_name="test",
            openai_proxy=proxy,
        )
        assert client.openai_proxy == proxy
        assert openai.proxy["http"] == proxy
        assert openai.proxy["https"] == proxy

    def test_params_setting(self):
        llm = OpenAI_Reasoning(
            api_token="test",
            azure_endpoint="test",
            api_version="test",
            deployment_name="Deployed-GPT-o1",
            is_chat_model=True,
            temperature=1.0,
            max_completion_tokens=50,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stop=None,
        )

        assert llm.deployment_name == "Deployed-GPT-o1"
        assert llm._is_chat_model
        assert llm.temperature == 1.0
        assert llm.max_completion_tokens == 50
        assert llm.top_p == 1.0
        assert llm.frequency_penalty == 0.0
        assert llm.presence_penalty == 0.0
        assert llm.stop == None

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
                "model": "gpt-35-turbo",
            }
        )

        openai = OpenAI_Reasoning(
            api_token="test",
            azure_endpoint="test",
            api_version="test",
            deployment_name="test",
        )
        mocker.patch.object(openai, "completion", return_value=expected_response)
        result = openai.completion("Some prompt.")

        openai.completion.assert_called_once_with("Some prompt.")
        assert result == expected_response

    def test_chat_completion(self, mocker):
        openai = OpenAI_Reasoning(
            api_token="test",
            azure_endpoint="test",
            api_version="test",
            deployment_name="test",
            is_chat_model=True,
        )
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

        mocker.patch.object(openai, "chat_completion", return_value=expected_response)

        result = openai.chat_completion("Hi")
        openai.chat_completion.assert_called_once_with("Hi")
        assert result == expected_response
