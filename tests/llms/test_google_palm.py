"""Unit tests for the openai LLM class"""
import re

import pytest
from google import generativeai

from pandasai.exceptions import APIKeyNotFoundError
from pandasai.llm.google_palm import GooglePalm


class MockedCompletion:
    def __init__(self, result: str):
        self.result = result


class TestGooglePalm:
    """Unit tests for the GooglePalm LLM class"""

    def test_type_without_token(self):
        with pytest.raises(APIKeyNotFoundError):
            GooglePalm(api_key="")

    def test_type_with_token(self):
        assert GooglePalm(api_key="test").type == "google-palm"

    def test_params_setting(self):
        llm = GooglePalm(
            api_key="test",
            model="models/text-bison-001",
            temperature=0.5,
            top_p=1.0,
            top_k=0.5,
            max_output_tokens=64,
        )

        assert llm.model == "models/text-bison-001"
        assert llm.temperature == 0.5
        assert llm.top_p == 1.0
        assert llm.top_k == 0.5
        assert llm.max_output_tokens == 64

    def test_validations(self):
        with pytest.raises(
            ValueError, match=re.escape("temperature must be in the range [0.0, 1.0]")
        ):
            GooglePalm(api_key="test", temperature=-1).call("Hello", "World")

        with pytest.raises(
            ValueError, match=re.escape("temperature must be in the range [0.0, 1.0]")
        ):
            GooglePalm(api_key="test", temperature=1.1).call("Hello", "World")

        with pytest.raises(
            ValueError, match=re.escape("top_p must be in the range [0.0, 1.0]")
        ):
            GooglePalm(api_key="test", top_p=-1).call("Hello", "World")

        with pytest.raises(
            ValueError, match=re.escape("top_p must be in the range [0.0, 1.0]")
        ):
            GooglePalm(api_key="test", top_p=1.1).call("Hello", "World")

        with pytest.raises(
            ValueError, match=re.escape("top_k must be in the range [0.0, 1.0]")
        ):
            GooglePalm(api_key="test", top_k=-1).call("Hello", "World")

        with pytest.raises(
            ValueError, match=re.escape("top_k must be in the range [0.0, 1.0]")
        ):
            GooglePalm(api_key="test", top_k=1.1).call("Hello", "World")

        with pytest.raises(
            ValueError, match=re.escape("max_output_tokens must be greater than zero")
        ):
            GooglePalm(api_key="test", max_output_tokens=0).call("Hello", "World")

        with pytest.raises(ValueError, match=re.escape("model is required.")):
            GooglePalm(api_key="test", model="").call("Hello", "World")

    def test_text_generation(self, mocker):
        llm = GooglePalm(api_key="test")
        expected_text = "This is the expected text."
        expected_response = MockedCompletion(expected_text)
        mocker.patch.object(
            generativeai, "generate_text", return_value=expected_response
        )

        result = llm._generate_text("Hi")
        assert result == expected_text

    def test_call(self, mocker):
        llm = GooglePalm(api_key="test")
        expected_text = "This is the expected text."
        expected_response = MockedCompletion(expected_text)
        mocker.patch.object(
            generativeai, "generate_text", return_value=expected_response
        )

        result = llm.call(instruction="hello", value="world", suffix="!")
        assert result == expected_text
