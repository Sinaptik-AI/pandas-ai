""" Starcoder LLM
This module is to run the StartCoder API hosted and maintained by HuggingFace.co.
To generate HF_TOKEN go to https://huggingface.co/settings/tokens after creating Account
on the platform.

Example:
    Use below example to call Starcoder Model

    >>> from pandasai.llm.starcoder import Starcoder
"""
import warnings

from ..helpers import load_dotenv
from .base import HuggingFaceLLM

load_dotenv()


class Starcoder(HuggingFaceLLM):

    """Starcoder LLM API (Deprecated: Kept for backwards compatibility)"""

    api_token: str
    _api_url: str = "https://api-inference.huggingface.co/models/bigcode/starcoder"
    _max_retries: int = 30

    def __init__(self, **kwargs):
        warnings.warn(
            """Starcoder is deprecated and will be removed in a future release.
            Please use langchain.llms.HuggingFaceHub instead, although please be 
            aware that it may perform poorly.
            """
        )
        super().__init__(**kwargs)

    @property
    def type(self) -> str:
        return "starcoder"
