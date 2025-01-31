import os
from typing import Any, Callable, Dict, Optional, Union

import openai

from pandasai.exceptions import APIKeyNotFoundError, MissingModelError
from pandasai.helpers import load_dotenv

from .base import BaseOpenAI

load_dotenv()


class AzureOpenAI(BaseOpenAI):
    """OpenAI LLM via Microsoft Azure
    This class uses `BaseOpenAI` class to support Azure OpenAI features.
    """

    azure_endpoint: Union[str, None] = None
    """Your Azure Active Directory token.
        Automatically inferred from env var `AZURE_OPENAI_AD_TOKEN` if not provided.
        For more: 
        https://www.microsoft.com/en-us/security/business/identity-access/microsoft-entra-id.
    """
    azure_ad_token: Union[str, None] = None
    """A function that returns an Azure Active Directory token.
        Will be invoked on every request.
    """
    azure_ad_token_provider: Union[Callable[[], str], None] = None
    deployment_name: str
    api_version: str = ""
    """Legacy, for openai<1.0.0 support."""
    api_base: str
    """Legacy, for openai<1.0.0 support."""
    api_type: str = "azure"

    def __init__(
        self,
        api_token: Optional[str] = None,
        azure_endpoint: Union[str, None] = None,
        azure_ad_token: Union[str, None] = None,
        azure_ad_token_provider: Union[Callable[[], str], None] = None,
        api_base: Optional[str] = None,
        api_version: Optional[str] = None,
        deployment_name: str = None,
        is_chat_model: bool = True,
        http_client: str = None,
        **kwargs,
    ):
        """
        __init__ method of AzureOpenAI Class.

        Args:
            api_token (str): Azure OpenAI API token.
            azure_endpoint (str): Azure endpoint.
                It should look like the following:
                <https://YOUR_RESOURCE_NAME.openai.azure.com/>
            azure_ad_token (str): Your Azure Active Directory token.
                Automatically inferred from env var `AZURE_OPENAI_AD_TOKEN` if not provided.
                For more: https://www.microsoft.com/en-us/security/business/identity-access/microsoft-entra-id.
            azure_ad_token_provider (str): A function that returns an Azure Active Directory token.
                Will be invoked on every request.
            api_version (str): Version of the Azure OpenAI API.
                Be aware the API version may change.
            api_base (str): Legacy, kept for backward compatibility with openai < 1.0.
                Ignored for openai >= 1.0.
            deployment_name (str): Custom name of the deployed model
            is_chat_model (bool): Whether ``deployment_name`` corresponds to a Chat
                or a Completion model.
            **kwargs: Inference Parameters.
        """

        self.api_token = (
            api_token
            or os.getenv("AZURE_OPENAI_API_KEY")
            or os.getenv("OPENAI_API_KEY")
        )
        self.azure_endpoint = azure_endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_base = api_base or os.getenv("OPENAI_API_BASE")
        self.api_version = api_version or os.getenv("OPENAI_API_VERSION")
        if self.api_token is None:
            raise APIKeyNotFoundError(
                "Azure OpenAI key is required. Please add an environment variable "
                "`AZURE_OPENAI_API_KEY` or `OPENAI_API_KEY` or pass `api_token` as a named parameter"
            )
        if self.azure_endpoint is None:
            raise APIKeyNotFoundError(
                "Azure endpoint is required. Please add an environment variable "
                "`AZURE_OPENAI_API_ENDPOINT` or pass `azure_endpoint` as a named parameter"
            )

        if self.api_version is None:
            raise APIKeyNotFoundError(
                "Azure OpenAI version is required. Please add an environment variable "
                "`OPENAI_API_VERSION` or pass `api_version` as a named parameter"
            )

        if deployment_name is None:
            raise MissingModelError(
                "No deployment name provided.",
                "Please include deployment name from Azure dashboard.",
            )
        self.azure_ad_token = azure_ad_token or os.getenv("AZURE_OPENAI_AD_TOKEN")
        self.azure_ad_token_provider = azure_ad_token_provider
        self._is_chat_model = is_chat_model
        self.deployment_name = deployment_name
        self.http_client = http_client

        self.openai_proxy = kwargs.get("openai_proxy") or os.getenv("OPENAI_PROXY")
        if self.openai_proxy:
            openai.proxy = {"http": self.openai_proxy, "https": self.openai_proxy}

        self._set_params(**kwargs)
        # set the client
        if self._is_chat_model:
            self.client = openai.AzureOpenAI(**self._client_params).chat.completions
        else:
            self.client = openai.AzureOpenAI(**self._client_params).completions

    @property
    def _default_params(self) -> Dict[str, Any]:
        """
        Get the default parameters for calling OpenAI API.

        Returns:
            dict: A dictionary containing Default Params.

        """
        return {
            **super()._default_params,
            "model": self.deployment_name,
        }

    @property
    def _client_params(self) -> Dict[str, any]:
        client_params = {
            "api_version": self.api_version,
            "azure_endpoint": self.azure_endpoint,
            "azure_deployment": self.deployment_name,
            "azure_ad_token": self.azure_ad_token,
            "azure_ad_token_provider": self.azure_ad_token_provider,
            "api_key": self.api_token,
            "http_client": self.http_client,
        }
        return {**client_params, **super()._client_params}

    @property
    def type(self) -> str:
        return "azure-openai"
