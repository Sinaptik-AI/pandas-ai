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
            """Starcoder has been deprecated as of version 1.5.
            Please choose a different LLM instead from the ones listed in
            https://docs.pandas-ai.com/en/latest/API/llms/
            """
        )

    @property
    def type(self) -> str:
        return "starcoder"
