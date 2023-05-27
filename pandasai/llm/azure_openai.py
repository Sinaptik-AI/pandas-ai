"""OpenAI LLM via Microsoft Azure Cloud"""

import os
from typing import Any, Dict, Optional

import openai
from dotenv import load_dotenv
from openai import InvalidRequestError
from openai.error import APIConnectionError

from ..exceptions import APIKeyNotFoundError, UnsupportedOpenAIModelError
from .base import BaseOpenAI

load_dotenv()


class AzureOpenAI(BaseOpenAI):
    """OpenAI LLM via Microsoft Azure"""

    api_base: str
    api_type: str = "azure"
    api_version: str
    engine: str

    def __init__(
        self,
        api_token: Optional[str] = None,
        api_base: Optional[str] = None,
        api_version: Optional[str] = None,
        deployment_name: str = None,
        **kwargs,
    ):
        """

        Args:
            api_token (str): Azure OpenAI API token.
            api_base (str): Base url of the Azure endpoint.
                It should look like the following: <https://YOUR_RESOURCE_NAME.openai.azure.com/>
            api_version (str): Version of the Azure OpenAI API.
                    Be aware the API version may change.
            deployment_name (str): Custom name of the deployed model
            is_completion_model (bool): Whether `deployment_name` corresponds to
                a model for completion or chat.
            **kwargs: Inference parameters
        """
        self.api_token = api_token or os.getenv("AZURE_OPENAI_KEY") or None
        self.api_base = api_base or os.getenv("AZURE_OPENAI_ENDPOINT") or None
        self.api_version = api_version or "2023-03-15-preview"
        if self.api_token is None:
            raise APIKeyNotFoundError("Azure OpenAI key is required")
        if self.api_base is None:
            raise APIKeyNotFoundError("Azure OpenAI base endpoint is required")

        openai.api_key = self.api_token
        openai.api_base = self.api_base
        openai.api_version = self.api_version
        openai.api_type = self.api_type

        if deployment_name is None:
            raise UnsupportedOpenAIModelError("Model deployment name is required.")
        try:
            model_name = openai.Deployment.retrieve(deployment_name).model
            model_capabilities = openai.Model.retrieve(model_name).capabilities
            if (
                not model_capabilities.completion
                and not model_capabilities.chat_completion
            ):
                raise UnsupportedOpenAIModelError(
                    "Model deployment name does not correspond to a "
                    "chat nor a completion model."
                )
            self.is_chat_model = model_capabilities.chat_completion
            self.engine = deployment_name
        except InvalidRequestError as ex:
            raise UnsupportedOpenAIModelError(
                "Model deployment name does not correspond to a valid model entity."
            ) from ex
        except APIConnectionError as ex:
            raise UnsupportedOpenAIModelError(
                f"Invalid Azure OpenAI Base Endpoint {api_base}"
            ) from ex

        self._set_params(**kwargs)

    @property
    def _default_params(self) -> Dict[str, Any]:
        """Get the default parameters for calling OpenAI API"""
        return {**super()._default_params, "engine": self.engine}

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

        if self.is_chat_model:
            response = self.chat_completion(str(instruction) + str(value) + suffix)
        else:
            response = self.completion(str(instruction) + str(value) + suffix)

        return response

    @property
    def type(self) -> str:
        return "azure-openai"
