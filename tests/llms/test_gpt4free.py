"""Unit tests for the Gpt4free LLM class"""
import g4f
import pytest

from pandasai.llm import Gpt4free
from pandasai.prompts import AbstractPrompt


class TestGpt4freeLLM:
    """Unit tests for the Gpt4free LLM class"""

    @pytest.fixture
    def prompt(self):
        class MockAbstractPrompt(AbstractPrompt):
            template: str = "instruction"

        return MockAbstractPrompt()

    def test_type(self):
        assert Gpt4free().type == "gpt4free"

    def test_call(self, mocker, prompt):
        g4f_mock = mocker.patch("g4f.ChatCompletion.create")
        expected_response = {"choices": [{"text": "Generated text."}]}
        g4f_mock.return_value = g4f.ChatCompletion.construct_from(expected_response)

        gpt4free = Gpt4free(model="gpt-3.5-turbo")
        result = gpt4free.call(instruction=prompt)

        g4f_mock.assert_called_once_with(
            model=gpt4free.model,
            provider=gpt4free.provider,
            messages=[{"role": "user", "content": prompt.to_string()}],
        )

        assert result == expected_response
