""" Unit tests for the IBMwatsonx class. """
import pytest
from ibm_watsonx_ai.wml_client_error import WMLClientError

from pandasai.exceptions import APIKeyNotFoundError
from pandasai.llm import IBMwatsonx


class TestIBMwatsonx:
    """Unit tests for the IBMwatsonx class."""

    def test_without_key(self):
        with pytest.raises(APIKeyNotFoundError):
            IBMwatsonx()

    def test_without_url(self):
        with pytest.raises(APIKeyNotFoundError):
            IBMwatsonx(api_key="test")

    def test_without_project_id(self):
        with pytest.raises(APIKeyNotFoundError):
            IBMwatsonx(api_key="test", url="http://test.com")

    def test_watsonx_invalid_model(self):
        with pytest.raises(WMLClientError):
            IBMwatsonx(
                api_key="test",
                watsonx_url="https://us-south.ml.cloud.ibm.com",
                watsonx_project_id="test",
                model="invalid_model",
            )

    def test_watsonx_invalid_params(self):
        # pass a parameter called top_m which is not valid
        with pytest.raises(KeyError):
            IBMwatsonx(
                api_key="test",
                watsonx_url="https://us-south.ml.cloud.ibm.com",
                watsonx_project_id="test",
                top_m=4,
            )
