""" Starcoder LLM """

import os
from typing import Optional

from dotenv import load_dotenv

from ..exceptions import APIKeyNotFoundError
from .base_hf import HuggingFaceLLM

load_dotenv()


class Starcoder(HuggingFaceLLM):
    """Starcoder LLM"""

    api_token: str
    _api_url: str = "https://api-inference.huggingface.co/models/bigcode/starcoder"
    _max_retries: int = 5

    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token or os.getenv("HUGGINGFACE_API_KEY") or None
        if self.api_token is None:
            raise APIKeyNotFoundError("HuggingFace Hub API key is required")

    @property
    def type(self) -> str:
        return "starcoder"
