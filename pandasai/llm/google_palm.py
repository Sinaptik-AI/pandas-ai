"""Google Palm LLM

This module is to run the Google PaLM API hosted and maintained by Google.
To read more on Google PaLM follow
https://developers.generativeai.google/products/palm.

Example:
    Use below example to call GooglePalm Model

    >>> from pandasai.llm.google_palm import GooglePalm
"""
from .base import BaseGoogle
from typing import Any
from ..helpers.optional import import_dependency
from ..exceptions import APIKeyNotFoundError


class GooglePalm(BaseGoogle):
    """Google Palm LLM
    BaseGoogle class is extended for Google Palm model. The default and only model
    support at the moment is models/text-bison-001.

    """

    model: str = "models/text-bison-001"
    google_palm: Any

    def __init__(self, api_key: str, **kwargs):
        """
        __init__ method of GooglePalm Class
        Args:
            api_key (str): API Key
            **kwargs: Extended Parameters inferred from BaseGoogle Class
        """
        self._configure(api_key=api_key)
        self._set_params(**kwargs)

    def _configure(self, api_key: str):
        """
        Configure Google Palm API Key
        Args:
            api_key (str): A string of API keys generated from Google Cloud.

        Returns:
            None.
        """

        if not api_key:
            raise APIKeyNotFoundError("Google Palm API key is required")

        err_msg = "Install google-generativeai >= 0.1 for Google Palm API"
        google_palm = import_dependency("google.generativeai", extra=err_msg)

        google_palm.configure(api_key=api_key)
        self.google_palm = google_palm

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
        completion = self.google_palm.generate_text(
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
