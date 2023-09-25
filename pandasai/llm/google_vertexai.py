"""Google VertexAI

This module is to run the Google VertexAI LLM.
To read more on VertexAI:
https://cloud.google.com/vertex-ai/docs/generative-ai/learn/generative-ai-studio.

Example:
    Use below example to call Google VertexAI

    >>> from pandasai.llm.google_palm import GoogleVertexAI

"""
from typing import Optional
from .base import BaseGoogle
from ..helpers.optional import import_dependency


class GoogleVertexAI(BaseGoogle):
    """Google Palm Vertexai LLM
    BaseGoogle class is extended for Google Palm model using Vertexai.
    The default model support at the moment is text-bison-001.
    However, user can choose to use code-bison-001 too.

    """

    def __init__(
        self, project_id: str, location: str, model: Optional[str] = None, **kwargs
    ):
        """
        A init class to implement the Google Vertexai Models

        Args:
            project_id (str): GCP project
            location (str): GCP project Location
            model Optional (str): Model to use Default to text-bison@001
            **kwargs: Arguments to control the Model Parameters
        """

        if model is None:
            self.model = "text-bison@001"
        else:
            self.model = model

        self._configure(project_id, location)
        self.project_id = project_id
        self.location = location
        self._set_params(**kwargs)

    def _configure(self, project_id: str, location: str):
        """
        Configure Google VertexAi. Set value `self.vertexai` attribute.

        Args:
            project_id (str): GCP Project.
            location (str): Location of Project.

        Returns:
            None.

        """

        err_msg = "Install google-cloud-aiplatform for Google Vertexai"
        vertexai = import_dependency("vertexai", extra=err_msg)
        vertexai.init(project=project_id, location=location)
        self.vertexai = vertexai

    def _valid_params(self):
        """Returns if the Parameters are valid or Not"""
        return super()._valid_params() + ["model"]

    def _validate(self):
        """
        A method to Validate the Model

        """

        super()._validate()

        if not self.model:
            raise ValueError("model is required.")

    def _generate_text(self, prompt: str) -> str:
        """
        Generates text for prompt.

        Args:
            prompt (str): A string representation of the prompt.

        Returns:
            str: LLM response.

        """
        self._validate()

        from vertexai.preview.language_models import (
            CodeGenerationModel,
            TextGenerationModel,
        )

        if self.model == "code-bison@001":
            code_generation = CodeGenerationModel.from_pretrained(self.model)

            completion = code_generation.predict(
                prefix=prompt,
                temperature=self.temperature,
                max_output_tokens=self.max_output_tokens,
            )
        else:
            text_generation = TextGenerationModel.from_pretrained(self.model)

            completion = text_generation.predict(
                prompt=prompt,
                temperature=self.temperature,
                top_p=self.top_p,
                top_k=self.top_k,
                max_output_tokens=self.max_output_tokens,
            )

        return str(completion)

    @property
    def type(self) -> str:
        return "google-vertexai"
