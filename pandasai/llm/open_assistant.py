""" Open Assistant LLM """

import os
from typing import Optional

from dotenv import load_dotenv

from ..exceptions import APIKeyNotFoundError
from .base_hf import HuggingFaceLLM

load_dotenv()


class OpenAssistant(HuggingFaceLLM):
    """Open Assistant LLM"""

    api_token: str
    _api_url: str = (
        "https://api-inference.huggingface.co/models/"
        "OpenAssistant/oasst-sft-1-pythia-12b"
    )
    _max_retries: int = 10

    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token or os.getenv("HUGGINGFACE_API_KEY") or None
        if self.api_token is None:
            raise APIKeyNotFoundError("HuggingFace Hub API key is required")

    @property
    def type(self) -> str:
        return "open-assistant"
