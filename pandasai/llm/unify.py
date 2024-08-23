"""Unify LLM API

This module is to run the Unify API using Unify's client.

Example:
    Use below example to call Unify Model

    >>> from pandasai.llm.unify import Unify
"""

import os
from typing import Any, Dict, Optional, Union

from ..exceptions import APIKeyNotFoundError, UnsupportedModelError
from ..helpers import load_dotenv
from .base import LLM

load_dotenv()

class Unify(LLM):
    """Unify LLM class.

    An API call to Unify API is sent and response is recorded and returned.
    """

    def __init__(
        self,
        api_token: Optional[str] = None,
        endpoint: Optional[str] = None,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize the Unify class.

        Args:
            api_token (str): API Token for Unify platform.
            endpoint (str): Endpoint name in format: <model_name>@<provider_name>
            model (str): Name of the model.
            provider (str): Name of the provider.
            **kwargs: Additional parameters for Unify client.
        """
        super().__init__()  # Initialize the base LLM class
        
        self.api_key = api_token or os.getenv("UNIFY_KEY")
        if not self.api_key:
            raise APIKeyNotFoundError("Unify API key is required")

        self.endpoint = endpoint
        self.model = model
        self.provider = provider

        if self.endpoint and (self.model or self.provider):
            raise ValueError("If endpoint is provided, model and provider should not be specified.")

        if self.endpoint:
            self.model, self.provider = self.endpoint.split("@")
        elif not (self.model and self.provider):
            raise ValueError("Both model and provider must be specified if endpoint is not provided.")

        # Store additional parameters
        self.additional_params = kwargs

        self._client = self._get_client()

    def _get_client(self):
        from unify.clients import Unify as UnifyClient

        return UnifyClient(
            api_key=self.api_key,
            endpoint=self.endpoint,
            model=self.model,
            provider=self.provider,
            **self.additional_params
        )

    def chat_completion(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Generate chat completion using Unify API.

        Args:
            prompt (str): The prompt to generate completion for.
            **kwargs: Additional parameters for the API call.

        Returns:
            Dict[str, Any]: The response from the API.
        """
        try:
            response = self._client.generate(
                user_prompt=prompt,
                max_tokens=kwargs.get("max_tokens", 1024),
                temperature=kwargs.get("temperature", 1.0),
                stop=kwargs.get("stop"),
            )
            return {"choices": [{"message": {"content": response}}]}
        except Exception as e:
            raise Exception(f"Error in Unify API call: {str(e)}")

    def call(self, instruction: str, value: str, suffix: str = "") -> str:
        """
        Call the Unify API to generate a response.

        Args:
            instruction (str): The instruction for the model.
            value (str): The value to be processed.
            suffix (str): Additional text to be appended to the prompt.

        Returns:
            str: The generated response from the model.
        """
        prompt = f"{instruction}\n\n{value}\n\n{suffix}".strip()
        response = self.chat_completion(prompt)
        return response["choices"][0]["message"]["content"]

    @property
    def type(self) -> str:
        return "unify"