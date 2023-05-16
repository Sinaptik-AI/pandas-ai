"""OpenAI LLM"""

import os
from typing import Any, Dict, Optional

import openai
from dotenv import load_dotenv

from ..exceptions import APIKeyNotFoundError, UnsupportedOpenAIModelError
from .base import BaseOpenAI

load_dotenv()


class OpenAI(BaseOpenAI):
    """OpenAI LLM"""

    _supported_chat_models = [
        "gpt-4",
        "gpt-4-0314",
        "gpt-4-32k",
        "gpt-4-32k-0314",
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-0301",
    ]
    _supported_completion_models = ["text-davinci-003"]

    model: str = "gpt-3.5-turbo"

    def __init__(
        self,
        api_token: Optional[str] = None,
        **kwargs,
    ):
        self.api_token = api_token or os.getenv("OPENAI_API_KEY") or None
        if self.api_token is None:
            raise APIKeyNotFoundError("OpenAI API key is required")
        openai.api_key = self.api_token

        self._set_params(**kwargs)

    @property
    def _default_params(self) -> Dict[str, Any]:
        """Get the default parameters for calling OpenAI API"""
        return {
            **super()._default_params,
            "model": self.model,
        }

    def call(self, instruction: str, value: str, suffix: str = "") -> str:
        """
        Call the OpenAI LLM.

        Args:
            instruction (str): Instruction to pass
            value (str): Value to pass
            suffix (str): Suffix to pass

        Raises:
            UnsupportedOpenAIModelError: Unsupported model

        Returns:
            str: Response
        """
        self.last_prompt = str(instruction) + str(value)

        if self.model in self._supported_completion_models:
            response = self.completion(str(instruction) + str(value) + suffix)
        elif self.model in self._supported_chat_models:
            response = self.chat_completion(str(instruction) + str(value) + suffix)
        else:
            raise UnsupportedOpenAIModelError("Unsupported model")

        return response

    @property
    def type(self) -> str:
        return "openai"
