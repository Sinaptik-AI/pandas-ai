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
from ..exceptions import UnsupportedModelError
from ..helpers.optional import import_dependency


class GoogleVertexAI(BaseGoogle):
    """Google Palm Vertexai LLM
    BaseGoogle class is extended for Google Palm model using Vertexai.
    The default model support at the moment is text-bison-001.
    However, user can choose to use code-bison-001 too.
    """

    _supported_code_models = [
        "code-bison",
        "code-bison-32k",
        "code-bison-32k@002",
        "code-bison@001",
        "code-bison@002",
    ]
    _supported_text_models = [
        "text-bison",
        "text-bison-32k",
        "text-bison-32k@002",
        "text-bison@001",
        "text-bison@002",
        "text-unicorn@001",
    ]
    _supported_generative_models = [
        "gemini-pro",
    ]

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

        self.model = model or "text-bison@001"

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
        from vertexai.preview.generative_models import GenerativeModel

        if self.model in self._supported_code_models:
            code_generation = CodeGenerationModel.from_pretrained(self.model)

            completion = code_generation.predict(
                prefix=prompt,
                temperature=self.temperature,
                max_output_tokens=self.max_output_tokens,
            )
        elif self.model in self._supported_text_models:
            text_generation = TextGenerationModel.from_pretrained(self.model)

            completion = text_generation.predict(
                prompt=prompt,
                temperature=self.temperature,
                top_p=self.top_p,
                top_k=self.top_k,
                max_output_tokens=self.max_output_tokens,
            )
        elif self.model in self._supported_generative_models:
            model = GenerativeModel(self.model)
            responses = model.generate_content(
                [prompt],
                generation_config={
                    "max_output_tokens": self.max_output_tokens,
                    "temperature": self.temperature,
                    "top_p": self.top_p,
                    "top_k": self.top_k,
                },
            )

            completion = responses.candidates[0].content.parts[0]
        else:
            raise UnsupportedModelError(self.model)

        return completion.text

    @property
    def type(self) -> str:
        return "google-vertexai"
