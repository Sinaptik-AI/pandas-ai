import unittest
from unittest.mock import patch
from pandasai.llm.gpt4all import GPT4AllLLM


class TestGPT4AllLLM(unittest.TestCase):
    """Unit tests for the base GPT4All LLM class"""

    def setUp(self):
        self.model_name = "ggml-all-MiniLM-L6-v2-f16.bin"
        self.model_folder_path = None
        self.n_threads = 4
        self.gpt4all_model = GPT4AllLLM(
            model_name=self.model_name,
        )

    @patch("pandasai.llm.gpt4all.GPT4AllLLM._auto_download")
    def test_type(self, mock_download_model):
        mock_download_model.return_value = "/path/to/dummy/model.bin"
        mock_download_model.assert_not_called()
        assert self.gpt4all_model.type == "gpt4all"
