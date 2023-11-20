""" Falcon LLM
This module is to run the Falcon API hosted and maintained by HuggingFace.co.
To generate HF_TOKEN go to https://huggingface.co/settings/tokens after creating Account
on the platform.

Example:
    Use below example to call Falcon Model

    >>> from pandasai.llm.falcon import Falcon
"""
import warnings

from ..helpers import load_dotenv
from .base import HuggingFaceLLM

load_dotenv()


class Falcon(HuggingFaceLLM):
    """Falcon LLM API (Deprecated: Kept for backwards compatibility)"""

    api_token: str
    _api_url: str = (
        "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct"
    )
    _max_retries: int = 30

    def __init__(self, **kwargs):
        warnings.warn(
            """Falcon has been deprecated as of version 1.5.
            Please choose a different LLM instead from the ones listed in
            https://docs.pandas-ai.com/en/latest/API/llms/
            """
        )

    @property
    def type(self) -> str:
        return "falcon"
