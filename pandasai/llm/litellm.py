"""liteLLM LLM API
liteLLM adds support for Azure, OpenAI, Palm, Anthropic, Cohere Models
See support models: https://litellm.readthedocs.io/en/latest/supported/

This module is to call completion() for the user selected models

Example:
    Use below example to call liteLLM Model

    >>> from pandasai.llm.litellm import liteLLM
"""

import os
from typing import Any, Dict, Optional

import openai
from dotenv import load_dotenv

from ..exceptions import APIKeyNotFoundError, UnsupportedOpenAIModelError
from ..prompts.base import Prompt
from .base import BaseliteLLM

load_dotenv()


class liteLLM(BaseliteLLM):
    """liteLLM using BaseliteLLM Class.

    An API call to OpenAI API is sent and response is recorded and returned.
    The default model is **gpt-3.5-turbo**
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
        ################
        "text-davinci-003",
        #################
        "command-nightly",
        #################
        "claude-2",
        "claude-instant-1",
        #################
        ""
    ]

    model: str = "gpt-3.5-turbo"

    def __init__(
        self,
        api_token: Optional[str] = None,
        **kwargs,
    ):
        """
        __init__ method of liteLLM Class
        Args:
            api_token (str): API Token for OpenAI platform.
            **kwargs: Extended Parameters inferred from BaseOpenAI class

        Returns: Response generated from OpenAI API
        """

        """
        API keys must be set in .env / environment
        os.environ["OPENAI_API_KEY"]
        os.environ["COHERE_API_KEY"]
        specific info on what keys to use is here: https://litellm.readthedocs.io/en/latest/supported/

        """ 
        self._set_params(**kwargs)

    @property
    def _default_params(self) -> Dict[str, Any]:
        """Get the default parameters for calling liteLLM API"""
        return {
            **super()._default_params,
            "model": self.model,
        }

    def call(self, instruction: Prompt, value: str, suffix: str = "") -> str:
        """
        Call the Azure/OpenAI/Cohere/Anthropic/Google LLM using liteLLM

        Args:
            instruction (Prompt): Instruction to pass
            value (str): Value to pass
            suffix (str): Suffix to pass

        Raises:
            UnsupportedOpenAIModelError: Unsupported model

        Returns:
            str: Response
        """
        self.last_prompt = str(instruction) + str(value)
        if self.model in self._supported_chat_models:
            response = self.chat_completion(str(instruction) + str(value) + suffix)
        else:
            raise UnsupportedOpenAIModelError("Unsupported model")

        return response

    @property
    def type(self) -> str:
        return "litellm"
