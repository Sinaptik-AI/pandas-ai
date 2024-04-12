"""IBM watsonx

This module is to run the IBM watsonx LLM.

Example:
    Use below example to call IBM watsonx

    # >>> from pandasai.llm.ibm_watsonx import IBMWatsonx

"""
import os
from typing import Optional

from ibm_watsonx_ai.foundation_models import Model

from .base import LLM
from ..exceptions import APIKeyNotFoundError
from ..helpers import load_dotenv
from ..prompts.base import BasePrompt

from pandasai.pipelines.pipeline_context import PipelineContext

load_dotenv()


class IBMWatsonx(LLM):
    max_new_tokens: Optional[int] = 25

    def __init__(
            self,
            model: Optional[str] = None,
            api_key: Optional[str] = None,
            watsonx_url: Optional[str] = None,
            watsonx_instance_id: str = None,
            watsonx_project_id: str = None
    ):
        """
        __init__ method of IBMWatsonx class

        Args:
            api_key (str): watsonx API key
                 To determine apikey go to https://cloud.ibm.com/iam/apikeys
            watsonx_url (str): watsonx endpoint url
                You can find available urls here:
                https://ibm.github.io/watsonx-ai-python-sdk/setup_cloud.html#authentication
            watsonx_instance_id
        """
        self.model = model or "google/flan-ul2"

        self.api_key = (api_key or os.getenv("WATSONX_API_KEY"))
        self.watsonx_url = watsonx_url or os.getenv("WATSONX_URL")
        self.watsonx_instance_id = watsonx_instance_id or os.getenv("WATSONX_INSTANCE_ID")
        self.project_id = watsonx_project_id or os.getenv("WATSONX_PROJECT_ID")

        if self.api_key is None:
            raise APIKeyNotFoundError(
                "IBM watsonx API key is required. Please add an environment variable "
                "`WATSONX_API_KEY` or pass `api_key` as a named parameter. "
                "You can create one at https://cloud.ibm.com/iam/apikeys."
            )
        if self.watsonx_url is None:
            raise APIKeyNotFoundError(
                "IBM watsonx url is required. Please add an environment variable "
                "`WATSONX_URL` or pass `watsonx_url` as a named parameter."
                "Go to https://ibm.github.io/watsonx-ai-python-sdk/setup_cloud.html#authentication for more."
            )

        self._configure(api_key=self.api_key, url=self.watsonx_url, project_id=self.project_id)

    def _configure(self, api_key: str, url: str, project_id: str):

        self.client = Model(
            model_id=self.model,
            params={'max_new_tokens': 25},
            credentials={"apikey": api_key, "url": url},
            project_id=project_id
        )

    def call(self, instruction: BasePrompt, context: PipelineContext = None) -> str:
        prompt = instruction.to_string()
        memory = context.memory if context else None

        result = self.client.generate_text(prompt=prompt)

        return result

    @property
    def type(self) -> str:
        return "ibm-watsonx"
