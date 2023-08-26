""" Falcon LLM
This module is to run the Falcon API hosted and maintained by HuggingFace.co.
To generate HF_TOKEN go to https://huggingface.co/settings/tokens after creating Account
on the platform.

Example:
    Use below example to call Falcon Model

    >>> from pandasai.llm.falcon import Falcon
"""


from ..helpers import load_dotenv
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
    _max_retries: int = 30

    @property
    def type(self) -> str:
        return "falcon"
