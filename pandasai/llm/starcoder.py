""" Starcoder LLM
This module is to run the StartCoder API hosted and maintained by HuggingFace.co.
To generate HF_TOKEN go to https://huggingface.co/settings/tokens after creating Account
on the platform.

Example:
    Use below example to call Starcoder Model

    >>> from pandasai.llm.starcoder import Starcoder
"""


from ..helpers import load_dotenv
from .base import HuggingFaceLLM

load_dotenv()


class Starcoder(HuggingFaceLLM):

    """Starcoder LLM API

    A base HuggingFaceLLM class is extended to use Starcoder model.

    """

    api_token: str
    _api_url: str = "https://api-inference.huggingface.co/models/bigcode/starcoder"
    _max_retries: int = 30

    @property
    def type(self) -> str:
        return "starcoder"
