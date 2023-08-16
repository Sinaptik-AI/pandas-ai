"""Google Palm LLM

This module is to run the Google PaLM API hosted and maintained by Google.
To read more on Google PaLM follow
https://developers.generativeai.google/products/palm.

Example:
    Use below example to call GooglePalm Model

    >>> from pandasai.llm.google_palm import GooglePalm

Example:
    Use below example to call Google VertexAi

    >>> from pandasai.llm.google_palm import GoogleVertexai

"""
from typing import Optional

from .base import BaseGoogle


class GooglePalm(BaseGoogle):
    """Google Palm LLM
    BaseGoogle class is extended for Google Palm model. The default and only model
    support at the moment is models/text-bison-001.

    """

    model: str = "models/text-bison-001"

    def __init__(self, api_key: str, **kwargs):
        """
        __init__ method of GooglePalm Class
        Args:
            api_key (str): API Key
            **kwargs: Extended Parameters inferred from BaseGoogle Class
        """
        self._configure(api_key=api_key)
        self._set_params(**kwargs)

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
        Generates text for prompt

        Args:
            prompt (str): Prompt

        Returns:
            str: LLM response
        """
        self._validate()
        completion = self.genai.generate_text(
            model=self.model,
            prompt=prompt,
            temperature=self.temperature,
            top_p=self.top_p,
            top_k=self.top_k,
            max_output_tokens=self.max_output_tokens,
        )
        return completion.result

    @property
    def type(self) -> str:
        return "google-palm"


class GoogleVertexai(BaseGoogle):
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

        self._configurevertexai(project_id, location)
        self.project_id = project_id
        self.location = location
        self._set_params(**kwargs)

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
        Generates text for prompt

        Args:
            prompt (str): Prompt

        Returns:
            str: LLM response
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
