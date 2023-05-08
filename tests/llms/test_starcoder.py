"""Unit tests for the starcoder LLM class"""

import pytest

from pandasai.exceptions import APIKeyNotFoundError
from pandasai.llm.starcoder import Starcoder


class TestStarcoderLLM:
    """Unit tests for the Starcoder LLM class"""

    def test_type(self):
        assert Starcoder(api_token="test").type == "starcoder"

    def test_api_url(self):
        assert (
            Starcoder(api_token="test")._api_url
            == "https://api-inference.huggingface.co/models/bigcode/starcoder"
        )

    def test_init(self):
        with pytest.raises(APIKeyNotFoundError):
            Starcoder()
