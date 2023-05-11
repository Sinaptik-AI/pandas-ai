"""OpenAI LLM via Microsoft Azure Cloud"""

import os
from typing import Optional

import openai
from dotenv import load_dotenv

from ..exceptions import APIKeyNotFoundError, UnsupportedOpenAIModelError
from .base import LLM

load_dotenv()


class AzureOpenAI(LLM):
    """OpenAI LLM via Microsoft Azure"""
    api_token: str
    api_base: str
    api_version: str
    engine: str
    temperature: float = 0
    max_tokens: int = 512
    top_p: float = 1
    frequency_penalty: float = 0
    presence_penalty: float = 0.6
    stop: Optional[str] = None

    def __init__(
        self,
        api_token: Optional[str] = None,
        api_base: Optional[str] = None,
        api_version: Optional[str] = None,
        deployment_name: str = None,
        is_completion_model: Optional[bool] = False,
        **kwargs,
    ):
        """

        Args:
            api_token (str): Azure OpenAI API token
            api_base (str): Base url of the Azure endpoint
            api_version (str): Version of the Azure OpenAI API
            deployment_name (str): Custom name of the deployed model
            is_completion_model (bool): Whether `deployement_name` corresponds to 
                a model for completion or chat. 
            **kwargs: Inference parameters
        """
        self.api_token = api_token or os.getenv("AZURE_OPENAI_KEY") or None
        self.api_base = api_base or os.getenv("AZURE_OPENAI_ENDPOINT") or None
        self.api_version = api_version or '2023-03-15-preview'
        if self.api_token is None:
            raise APIKeyNotFoundError("Azure OpenAI key is required")
        elif self.api_base is None:
            raise APIKeyNotFoundError("Azure OpenAI base endpoint is required")

        openai.api_key = self.api_token
        openai.api_base = self.api_base
        openai.api_version = self.api_version
        openai.api_type = 'azure'

        if deployment_name is None:
            raise UnsupportedOpenAIModelError("Model deployment name is required.")
        self.engine = deployment_name
        self.is_completion_model = is_completion_model

        self._set_params(**kwargs)

    def _set_params(self, **kwargs):
        valid_params = [
            "engine",
            "temperature",
            "max_tokens",
            "top_p",
            "frequency_penalty",
            "presence_penalty",
            "stop",
        ]
        for key, value in kwargs.items():
            if key in valid_params:
                setattr(self, key, value)

    def completion(self, prompt: str) -> str:
        """
        Query the completion API

        Args:
            prompt (str): Prompt

        Returns:
            str: LLM response
        """
        params = {
            "engine": self.engine,
            "prompt": prompt,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
        }

        if self.stop is not None:
            params["stop"] = [self.stop]

        response = openai.Completion.create(**params)

        return response["choices"][0]["text"]

    def chat_completion(self, value: str) -> str:
        """
        Query the chat completion API

        Args:
            value (str): Prompt

        Returns:
            str: LLM response
        """
        params = {
            "engine": self.engine,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "messages": [
                {
                    "role": "system",
                    "content": value,
                }
            ],
        }

        if self.stop is not None:
            params["stop"] = [self.stop]

        response = openai.ChatCompletion.create(**params)

        return response["choices"][0]["message"]["content"]

    def call(self, instruction: str, value: str, suffix: str = "") -> str:
        """
        Call the Azure OpenAI LLM.

        Args:
            instruction (str): Instruction to pass
            value (str): Value to pass
            suffix(str): Suffix to pass

        Returns:
            str: Response
        """
        self.last_prompt = str(instruction) + str(value)

        if self.is_completion_model:
            response = self.completion(str(instruction) + str(value) + suffix)
        else:
            response = self.chat_completion(str(instruction) + str(value) + suffix)

        return response

    @property
    def type(self) -> str:
        return "azure-openai"
