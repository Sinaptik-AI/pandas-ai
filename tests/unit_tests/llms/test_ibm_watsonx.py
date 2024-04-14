""" Unit tests for the IBM watsonx class. """
from unittest.mock import MagicMock

import pytest

from pandasai.exceptions import APIKeyNotFoundError
from pandasai.llm import IBMwatsonx
from pandasai.prompts import BasePrompt


class TestIBMWatsonx:
    """ Unit tests for the IBMwatsonx class."""
    @pytest.fixture
    def prompt(self):
        class MockBasePrompt(BasePrompt):
            template: str = "Hello"

        return MockBasePrompt()

    def test_type_without_token(self):
        with pytest.raises(APIKeyNotFoundError):
            IBMwatsonx(api_key="")
    def test_type_with_token(self):
        assert IBMwatsonx(api_key="test").type == "ibm-watsonx"

    def test_params_setting(self):
        llm = IBMWatsonx(
            api_key="test",
            model="google/flan-ul2",
            temperature=0.6,
            top_p=1.0,
            top_k=50,
            max_new_tokens=100,
        )

        assert llm.model == "google/flan-ul2"
        assert llm.temperature == 0.6
        assert llm.top_p == 1.0
        assert llm.top_k == 50
        assert llm.max_new_tokens == 100

    def test_call(self, mocker, prompt):
        llm = IBMwatsonx(
            model_id=self.model,
            params=self._set_params,
            credentials={"apikey": "test", "url": "test_url"},
            project_id="test_project_id"
        )

        expected_text = "This is the expected text."
        expected_response = MockedCompletion(expected_text)
        mocker.patch.object(
            generativeai, "generate_text", return_value=expected_response
        )

        result = llm.call(instruction=prompt)
        assert result == expected_text
