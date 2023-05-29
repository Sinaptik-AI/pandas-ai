""" Starcoder LLM
This module is to run the StartCoder API hosted and maintained by HuggingFace.co.
To generate HF_TOKEN go to https://huggingface.co/settings/tokens after creating Account
on the platform.

Example:
    Use below example to call Starcoder Model

    >>> from pandasai.llm.starcoder import Starcoder
"""


import os
from typing import Optional

from dotenv import load_dotenv

from ..exceptions import APIKeyNotFoundError
from .base import HuggingFaceLLM

load_dotenv()


class Starcoder(HuggingFaceLLM):

    """Starcoder LLM API

    A base HuggingFaceLLM class is extended to use Starcoder model.

    """

    api_token: str
    _api_url: str = "https://api-inference.huggingface.co/models/bigcode/starcoder"
    _max_retries: int = 5

    def __init__(self, api_token: Optional[str] = None):
        """
        __init__ method of Starcoder Class
        Args:
            api_token (str): API token from Huggingface platform
        """

        self.api_token = api_token or os.getenv("HUGGINGFACE_API_KEY") or None
        if self.api_token is None:
            raise APIKeyNotFoundError("HuggingFace Hub API key is required")

    @property
    def type(self) -> str:
        return "starcoder"
