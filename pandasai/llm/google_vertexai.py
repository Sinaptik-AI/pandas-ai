"""Google VertexAI

This module is to run the Google VertexAI LLM.
To read more on VertexAI:
https://cloud.google.com/vertex-ai/docs/generative-ai/learn/generative-ai-studio.

Example:
    Use below example to call Google VertexAI

    >>> from pandasai.llm import GoogleVertexAI

"""
from typing import Optional, Dict, Any
from .base import BaseGoogle
from ..exceptions import UnsupportedModelError
from ..helpers.optional import import_dependency


def init_vertexai(
    project_id, location, credentials=None,
) -> None:
    vertexai = import_dependency(
        "vertexai",
        extra="Could not import VertexAI. Please, install "
              "it with `pip install google-cloud-aiplatform`"
    )
    init_params = {
        "project": project_id,
        "location": location,
        **({"credentials": credentials} if credentials is not None else {})
    }
    vertexai.init(**init_params)


class GoogleVertexAI(BaseGoogle):
    """Google Palm Vertexai LLM
    BaseGoogle class is extended for Google Palm model using Vertexai.
    The default model support at the moment is text-bison-001.
    However, user can choose to use code-bison-001 too.
    """

    _supported_code_models = [
        "code-bison",
        "code-bison-32k",
        "code-bison@001",
    ]
    _supported_text_models = [
        "text-bison",
        "text-bison-32k",
        "text-bison@001",
    ]
    model: str = "text-bison@001"

    def __init__(
            self,
            project_id: str,
            location: str,
            model: Optional[str] = None,
            credentials: Any = None,
            **kwargs
    ):
        """
        An init class to implement the Google Vertexai Models

        Args:
            project_id (str): GCP project to use when making Vertex API calls
            location (str): GCP project location to use when making Vertex API calls
            model (str): VertexAI Large Language Model to use. Default to text-bison@001
            credentials: The default custom credentials to use when making API calls.
                If not provided, credentials will be ascertained from the environment.
            **kwargs: Arguments to control the Model Parameters
        """
        init_vertexai(project_id, location, credentials)
        if model:
            self.model = model

        if self.model in self._supported_code_models:
            from vertexai.preview.language_models import CodeGenerationModel

            self.client = CodeGenerationModel.from_pretrained(self.model)
        elif self.model in self._supported_text_models:
            from vertexai.preview.language_models import TextGenerationModel

            self.client = TextGenerationModel.from_pretrained(self.model)
        else:
            raise UnsupportedModelError(self.model)
        self.project_id = project_id
        self.location = location
        self._set_params(**kwargs)
        self._validate()

    def _valid_params(self):
        """Returns if the Parameters are valid or Not"""
        return super()._valid_params() + ["model"]

    @property
    def _default_params(self) -> Dict[str, Any]:
        if "code" in self.model:
            return {
                "temperature": self.temperature,
                "max_output_tokens": self.max_output_tokens,
            }
        else:
            return {
                "temperature": self.temperature,
                "max_output_tokens": self.max_output_tokens,
                "top_k": self.top_k,
                "top_p": self.top_p,
            }

    def _generate_text(self, prompt: str) -> str:
        """
        Generates text for prompt.

        Args:
            prompt (str): A string representation of the prompt.

        Returns:
            str: LLM response.

        """
        completion = self.client.predict(
            prompt,
            **self._default_params
        )
        return str(completion)

    @property
    def type(self) -> str:
        return "google-vertexai"
