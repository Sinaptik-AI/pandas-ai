"""IBM watsonx

This module is for the IBM watsonx.ai large language models.

"""
from __future__ import annotations

import os
from typing import TYPE_CHECKING, Optional

from ..exceptions import APIKeyNotFoundError
from ..helpers import load_dotenv
from ..helpers.optional import import_dependency
from ..prompts.base import BasePrompt
from .base import LLM

if TYPE_CHECKING:
    from pandasai.pipelines.pipeline_context import PipelineContext


load_dotenv()


class IBMwatsonx(LLM):
    decoding_method: Optional[str] = None
    length_penalty: Optional[dict] = None
    repetition_penalty: Optional[int] = None
    stop_sequences: Optional[list] = None
    truncate_input_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    min_new_tokens: Optional[int] = None
    max_new_tokens: Optional[int] = None
    random_seed: Optional[int] = None

    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        watsonx_url: Optional[str] = None,
        watsonx_project_id: str = None,
        **kwargs,
    ):
        """
        __init__ method of IBMwatsonx class

        Args:
            api_key (str): watsonx API key
                 To determine apikey go to https://cloud.ibm.com/iam/apikeys
            watsonx_url (str): watsonx endpoint url
                Depends on which region the Watson Studio service was provisioned.
                You can find available urls here:
                https://ibm.github.io/watsonx-ai-python-sdk/setup_cloud.html#authentication
            project_id (str) : watsonx project id
                ID of the Watson Studio project
                You can copy the project_id from Project’s Manage tab (Project -> Manage -> General -> Details).
        """
        self.model = model or "ibm/granite-13b-chat-v2"

        self.api_key = api_key or os.getenv("WATSONX_API_KEY")
        self.project_id = watsonx_project_id or os.getenv("WATSONX_PROJECT_ID")
        self.watsonx_url = watsonx_url or os.getenv("WATSONX_URL")

        if self.api_key is None:
            raise APIKeyNotFoundError(
                "IBM watsonx API key is required. Please add an environment variable "
                "`WATSONX_API_KEY` or pass `api_key` as a named parameter. "
                "You can create one at https://cloud.ibm.com/iam/apikeys."
            )
        if self.watsonx_url is None:
            raise APIKeyNotFoundError(
                "IBM watsonx region url is required. Please add an environment variable "
                "`WATSONX_URL` or pass `watsonx_url` as a named parameter."
            )
        if self.project_id is None:
            raise APIKeyNotFoundError(
                "Project ID is required. Please add an environment variable "
                "`WATSONX_PROJECT_ID` or pass `project_id` as a named parameter."
                "The project ID can be found in the created Watson Studio resource in IBM Cloud."
            )
        self._set_params(**kwargs)
        self._configure(
            api_key=self.api_key, url=self.watsonx_url, project_id=self.project_id
        )

    def _configure(self, api_key: str, url: str, project_id: str):
        """
        Configure IBM watsonx.
        """
        from ibm_watsonx_ai.foundation_models import Model

        self.watsonx = Model(
            model_id=self.model,
            params={
                "decoding_method": self.decoding_method,
                "length_penalty": self.length_penalty,
                "repetition_penalty": self.repetition_penalty,
                "stop_sequences": self.stop_sequences,
                "temperature": self.temperature,
                "top_p": self.top_p,
                "top_k": self.top_k,
                "min_new_tokens": self.min_new_tokens,
                "max_new_tokens": self.max_new_tokens,
                "truncate_input_tokens": self.truncate_input_tokens,
                "random_seed": self.random_seed,
            },
            credentials={"apikey": api_key, "url": url},
            project_id=project_id,
        )

    def _set_params(self, **kwargs):
        """
        Dynamically set Parameters for the object.

        Args:
            **kwargs:
                Possible keyword arguments: "temperature", "top_p", "top_k",
                "max_output_tokens".

        Returns:
            None.

        """
        err_msg = "Install ibm-watsonx-ai for IBMwatsonx"
        import_dependency("ibm_watsonx_ai", extra=err_msg)

        from ibm_watsonx_ai.metanames import GenTextParamsMetaNames

        valid_params = GenTextParamsMetaNames().get_example_values().keys()
        for key, value in kwargs.items():
            if key in valid_params:
                setattr(self, key, value)
            else:
                raise KeyError(
                    f"Parameter {key} is invalid. Accepted parameters: {[*valid_params]}"
                )

    def call(self, instruction: BasePrompt, context: PipelineContext = None) -> str:
        prompt = instruction.to_string()

        memory = context.memory if context else None

        prompt = self.prepend_system_prompt(prompt, memory)

        self.last_prompt = prompt

        return self.watsonx.generate_text(prompt=prompt)

    @property
    def type(self) -> str:
        return "ibm-watsonx-ai"
