"""Unit tests for the falcon LLM class"""

from pandasai.llm import Falcon


class TestFalconLLM:
    """Unit tests for the Falcon LLM class"""

    def test_type(self):
        assert Falcon(api_token="test").type == "falcon"
