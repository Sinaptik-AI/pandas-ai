"""Unit tests for the Anthropic's LLM class"""
import pytest

from pandasai.exceptions import APIKeyNotFoundError
from pandasai.llm import Anthropic

class TestAnthropic:
    """Unit tests for the Anthropic LLM class"""

    def test_type_without_token(self):
        with pytest.raises(APIKeyNotFoundError):
            Anthropic(api_key="")

    def test_type_with_token(self):
        assert Anthropic(api_key="test").type == "anthropic"

    def test_params_setting(self):
        llm = Anthropic(
            api_key="test",
            model="claude-2",
            temperature=0.5,
            top_p=1.0,
            top_k=50,
            max_output_tokens=64,
        )

        assert llm.model == "claude-2"
        assert llm.temperature == 0.5
        assert llm.top_p == 1.0
        assert llm.top_k == 50
        assert llm.max_output_tokens == 64
