import unittest
from unittest.mock import MagicMock, patch

from pandasai.exceptions import PandasAIApiCallError
from pandasai.llm.bamboo_llm import BambooLLM
from pandasai.core.prompts.base import BasePrompt


class MockHttpResponse:
    def __init__(self, status_code):
        self.status_code = status_code

    def json(self):
        return {"answer": "Hello World", "message": "test"}


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
        assert call_args[2] == "/query"
        assert mock_request.call_args_list[0][1] == {
            "json": {
                "prompt": "instruction",
            }
        }

    @patch("pandasai.helpers.request.requests.request", autospec=True)
    def test_status_code_200(self, mock_request_lib):
        prompt = self.get_prompt()
        context = self.get_context()
        bllm = BambooLLM(api_key="dummy_key")
        mock_request_lib.return_value = MockHttpResponse(200)
        bllm.call(prompt, context)

    @patch("pandasai.helpers.request.requests.request", autospec=True)
    def test_status_code_not_200(self, mock_request_lib):
        prompt = self.get_prompt()
        context = self.get_context()
        bllm = BambooLLM(api_key="dummy_key")
        mock_request_lib.return_value = MockHttpResponse(400)
        with self.assertRaises(PandasAIApiCallError):
            bllm.call(prompt, context)
