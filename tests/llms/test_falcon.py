"""Unit tests for the falcon LLM class"""

import pytest

from pandasai.exceptions import APIKeyNotFoundError
from pandasai.llm.falcon import Falcon


class TestFalconLLM:
    """Unit tests for the Falcon LLM class"""

    def test_type(self):
        assert Falcon(api_token="test").type == "falcon"

    def test_init(self):
        with pytest.raises(APIKeyNotFoundError):
            Falcon()
