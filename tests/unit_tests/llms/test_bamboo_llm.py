import unittest
from unittest.mock import MagicMock, patch

from pandasai.llm.bamboo_llm import BambooLLM
from pandasai.prompts.base import BasePrompt


class TestBambooLLM(unittest.TestCase):
    def get_prompt(self):
        class MockBasePrompt(BasePrompt):
            template: str = "instruction"

            def to_json(self):
                return {
                    "code": ["print('Hello')", "for i in range(10): print(i)"],
                    "query": ["What is Chroma?", "How does it work?"],
                }

        return MockBasePrompt()

    def get_context(self):
        return MagicMock()

    @patch("pandasai.helpers.request.Session.make_request", autospec=True)
    def test_call_method(self, mock_request):
        prompt = self.get_prompt()
        context = self.get_context()
        bllm = BambooLLM(api_key="dummy_key")
        bllm.call(prompt, context)
        call_args = mock_request.call_args_list[0][0]
        mock_request.assert_called_once()
        assert call_args[1] == "POST"
        assert call_args[2] == "/llm/chat"
        assert mock_request.call_args_list[0][1] == {
            "json": {
                "code": ["print('Hello')", "for i in range(10): print(i)"],
                "query": ["What is Chroma?", "How does it work?"],
            }
        }
