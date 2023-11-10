"""Unit tests for the starcoder LLM class"""

from pandasai.llm import Starcoder


class TestStarcoderLLM:
    """Unit tests for the Starcoder LLM class"""

    def test_type(self):
        assert Starcoder(api_token="test").type == "starcoder"
