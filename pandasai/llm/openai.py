"""OpenAI LLM API

This module is to run the OpenAI API using OpenAI API.

Example:
    Use below example to call OpenAI Model

    >>> from pandasai.llm.openai import OpenAI
"""

import os
from typing import Any, Dict, Optional

import openai
from ..helpers import load_dotenv

from ..exceptions import APIKeyNotFoundError, UnsupportedOpenAIModelError
from ..prompts.base import AbstractPrompt
from .base import BaseOpenAI

load_dotenv()


class OpenAI(BaseOpenAI):
    """OpenAI LLM using BaseOpenAI Class.

    An API call to OpenAI API is sent and response is recorded and returned.
    The default chat model is **gpt-3.5-turbo**.
    The list of supported Chat models includes ["gpt-4", "gpt-4-0613", "gpt-4-32k",
     "gpt-4-32k-0613", "gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-3.5-turbo-0613",
     "gpt-3.5-turbo-16k-0613", "gpt-3.5-turbo-instruct"].
    The list of supported Completion models includes "gpt-3.5-turbo-instruct" and
     "text-davinci-003" (soon to be deprecated).
    """

    _supported_chat_models = [
        "gpt-4",
        "gpt-4-0613",
        "gpt-4-32k",
        "gpt-4-32k-0613",
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-16k",
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-16k-0613",
    ]
    _supported_completion_models = ["text-davinci-003", "gpt-3.5-turbo-instruct"]

    model: str = "gpt-3.5-turbo"

    def __init__(
        self,
        api_token: Optional[str] = None,
        api_key_path: Optional[str] = None,
        **kwargs,
    ):
        """
        __init__ method of OpenAI Class

        Args:
            api_token (str): API Token for OpenAI platform.
            **kwargs: Extended Parameters inferred from BaseOpenAI class

        """
        self.api_token = api_token or os.getenv("OPENAI_API_KEY") or None
        self.api_key_path = api_key_path

        if (not self.api_token) and (not self.api_key_path):
            raise APIKeyNotFoundError("Either OpenAI API key or key path is required")

        if self.api_token:
            openai.api_key = self.api_token
        else:
            openai.api_key_path = self.api_key_path

        self.openai_proxy = kwargs.get("openai_proxy") or os.getenv("OPENAI_PROXY")
        if self.openai_proxy:
            openai.proxy = {"http": self.openai_proxy, "https": self.openai_proxy}

        self._set_params(**kwargs)

    @property
    def _default_params(self) -> Dict[str, Any]:
        """Get the default parameters for calling OpenAI API"""
        return {
            **super()._default_params,
            "model": self.model,
        }

    def call(self, instruction: AbstractPrompt, suffix: str = "") -> str:
        """
        Call the OpenAI LLM.

        Args:
            instruction (AbstractPrompt): A prompt object with instruction for LLM.
            suffix (str): Suffix to pass.

        Raises:
            UnsupportedOpenAIModelError: Unsupported model

        Returns:
            str: Response
        """
        self.last_prompt = instruction.to_string() + suffix

        if self.model in self._supported_chat_models:
            response = self.chat_completion(self.last_prompt)
        elif self.model in self._supported_completion_models:
            response = self.completion(self.last_prompt)
        else:
            raise UnsupportedOpenAIModelError("Unsupported model")

        return response

    @property
    def type(self) -> str:
        return "openai"
