"""Unit tests for the base huggignface LLM class"""

import pytest
import requests

from pandasai.llm.base_hf import HuggingFaceLLM


class TestBaseHfLLM:
    """Unit tests for the huggingface LLM class"""

    @pytest.fixture
    def api_response(self):
        return [{"generated_text": "Some text"}]

    def test_type(self):
        assert HuggingFaceLLM().type == "huggingface-llm"

    def test_api_url(self):
        assert (
            HuggingFaceLLM()._api_url == "https://api-inference.huggingface.co/models/"
        )

    def test_query(self, mocker, api_response):
        response_mock = mocker.Mock()
        response_mock.json.return_value = api_response
        mocker.patch("requests.post", return_value=response_mock)

        # Call the query method
        llm = HuggingFaceLLM()
        llm.api_token = "test_token"
        payload = {"inputs": "Some input text"}
        result = llm.query(payload)

        # Check that the mock was called correctly
        requests.post.assert_called_once_with(
            llm._api_url,
            headers={"Authorization": "Bearer test_token"},
            json=payload,
            timeout=60,
        )

        # Check that the result is correct
        assert result == api_response[0]["generated_text"]

    def test_call(self, mocker):
        huggingface = HuggingFaceLLM()
        huggingface.api_token = "test_token"

        mocker.patch.object(huggingface, "call", return_value="Generated text")

        result = huggingface.call("instruction", "value", "suffix")
        assert result == "Generated text"
