""" Falcon LLM
This module is to run the Falcon API hosted and maintained by HuggingFace.co.
To generate HF_TOKEN go to https://huggingface.co/settings/tokens after creating Account
on the platform.

Example:
    Use below example to call Falcon Model

    >>> from pandasai.llm.falcon import Falcon
"""


import os
from typing import Optional

from dotenv import load_dotenv

from ..exceptions import APIKeyNotFoundError
from .base import HuggingFaceLLM

load_dotenv()


class Falcon(HuggingFaceLLM):

    """Falcon LLM API

    A base HuggingFaceLLM class is extended to use Falcon model.

    """

    api_token: str
    _api_url: str = (
        "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct"
    )
    _max_retries: int = 5

    def __init__(self, api_token: Optional[str] = None):
        """
        __init__ method of Falcon Class
        Args:
            api_token (str): API token from Huggingface platform
        """

        self.api_token = api_token or os.getenv("HUGGINGFACE_API_KEY") or None
        if self.api_token is None:
            raise APIKeyNotFoundError("HuggingFace Hub API key is required")

    @property
    def type(self) -> str:
        return "falcon"
