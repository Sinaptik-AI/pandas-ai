""" Open Assistant LLM

This module is to run the HuggingFace OpenAssistant API hosted and maintained by
HuggingFace.co. To generate HF_TOKEN go to https://huggingface.co/settings/tokens after
creating Account on the platform.

Example:
    Use below example to call Starcoder Model

    >>> from pandasai.llm.open_assistant import OpenAssistant
"""

import os
from typing import Optional

from dotenv import load_dotenv

from ..exceptions import APIKeyNotFoundError
from .base import HuggingFaceLLM

load_dotenv()


class OpenAssistant(HuggingFaceLLM):
    """Open Assistant LLM
    A base HuggingFaceLLM class is extended to use OpenAssistant Model via its API.
    Currently `oasst-sft-1-pythia-12b` is supported via this module.
    """

    api_token: str
    _api_url: str = (
        "https://api-inference.huggingface.co/models/"
        "OpenAssistant/oasst-sft-1-pythia-12b"
    )
    _max_retries: int = 10

    def __init__(self, api_token: Optional[str] = None):
        """
        __init__ method of OpenAssistant Calss

        Raises:
            APIKeyNotFoundError: HuggingFace Hub API key is required

        Args:
            api_token (str): API token from Huggingface platform
        """
        self.api_token = api_token or os.getenv("HUGGINGFACE_API_KEY") or None
        if self.api_token is None:
            raise APIKeyNotFoundError("HuggingFace Hub API key is required")

    @property
    def type(self) -> str:
        return "open-assistant"
