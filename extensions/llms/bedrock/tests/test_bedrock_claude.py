"""Unit tests for the openai LLM class"""

import io
import json
from unittest.mock import MagicMock

import pytest

from extensions.llms.bedrock.pandasai_bedrock.claude import BedrockClaude
from pandasai.core.prompts.base import BasePrompt
from pandasai.exceptions import APIKeyNotFoundError, UnsupportedModelError


class MockBedrockRuntimeClient:
    def invoke_model(self, **kwargs):
        text = json.dumps({"content": [{"text": "This is the expected text."}]})
        text = io.StringIO(text)
        return {"body": text}


class MockedCompletion:
    def __init__(self, result: str):
        self.result = result


class TestBedrockClaude:
    """Unit tests for the BedrockClaude LLM class"""

    @pytest.fixture
    def prompt(self):
        class MockBasePrompt(BasePrompt):
            template: str = "Hello"

        return MockBasePrompt()

    @pytest.fixture
    def context(self):
        return MagicMock()

    def test_type_without_bedrockclient(self):
        with pytest.raises(APIKeyNotFoundError):
            BedrockClaude(bedrock_runtime_client="abc")

    def test_type_with_token(self):
        assert (
            BedrockClaude(bedrock_runtime_client=MockBedrockRuntimeClient()).type
            == "bedrock-claude"
        )

    def test_unsupported_models(self):
        with pytest.raises(UnsupportedModelError):
            BedrockClaude(
                bedrock_runtime_client=MockBedrockRuntimeClient(), model="abc"
            )

    def test_params_setting(self):
        llm = BedrockClaude(
            bedrock_runtime_client=MockBedrockRuntimeClient(),
            model="anthropic.claude-3-sonnet-20240229-v1:0",
            temperature=0.5,
            top_p=1.0,
            max_tokens=64,
        )

        assert llm.model == "anthropic.claude-3-sonnet-20240229-v1:0"
        assert llm.temperature == 0.5
        assert llm.top_p == 1.0
        assert llm.top_k is None
        assert llm.max_tokens == 64

    def test_call(self, prompt):
        llm = BedrockClaude(bedrock_runtime_client=MockBedrockRuntimeClient())
        expected_text = "This is the expected text."
        result = llm.call(instruction=prompt)
        assert result == expected_text
