import os
from typing import Any, Dict, Optional

import openai

from pandasai.exceptions import APIKeyNotFoundError, UnsupportedModelError
from pandasai.helpers import load_dotenv

from pandasai_openai.base import BaseOpenAI

load_dotenv()


class MiniMax(BaseOpenAI):
    """MiniMax LLM using BaseOpenAI Class.

    MiniMax provides an OpenAI-compatible API. This class connects to MiniMax's
    API endpoint and supports MiniMax chat models.

    The default model is **MiniMax-M3** (512K context, 128K max output, supports
    image input). Supported models include: MiniMax-M3, MiniMax-M2.7,
    MiniMax-M2.7-highspeed.
    """

    _supported_chat_models = [
        "MiniMax-M3",
        "MiniMax-M2.7",
        "MiniMax-M2.7-highspeed",
    ]

    model: str = "MiniMax-M3"
    api_base: str = "https://api.minimax.io/v1"
    temperature: float = 0.1

    def __init__(
        self,
        api_token: Optional[str] = None,
        **kwargs,
    ):
        """
        __init__ method of MiniMax Class.

        Args:
            api_token (str): API Token for MiniMax platform.
                Can also be set via MINIMAX_API_KEY environment variable.
            **kwargs: Extended Parameters inferred from BaseOpenAI class.
        """
        self.api_token = api_token or os.getenv("MINIMAX_API_KEY") or None

        if not self.api_token:
            raise APIKeyNotFoundError("MiniMax API key is required")

        self.api_base = (
            kwargs.get("api_base")
            or os.getenv("MINIMAX_API_BASE")
            or self.api_base
        )

        self.openai_proxy = kwargs.get("openai_proxy") or os.getenv("OPENAI_PROXY")
        if self.openai_proxy:
            openai.proxy = {"http": self.openai_proxy, "https": self.openai_proxy}

        self._set_params(**kwargs)

        if self.model not in self._supported_chat_models:
            raise UnsupportedModelError(self.model)

        self._is_chat_model = True
        self.client = openai.OpenAI(**self._client_params).chat.completions

    @property
    def _default_params(self) -> Dict[str, Any]:
        """Get the default parameters for calling MiniMax API."""
        return {
            **super()._default_params,
            "model": self.model,
        }

    @property
    def type(self) -> str:
        return "minimax"
