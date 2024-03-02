"""Google Gemini LLM

This module is to run the Google Gemini API hosted and maintained by Google.
To read more on Google Gemini follow
https://ai.google.dev/docs/gemini_api_overview.

Example:
    Use below example to call GoogleGemini Model

    >>> from pandasai.llm.google_gemini import GoogleGemini
"""
from typing import Any, Optional

from ..exceptions import APIKeyNotFoundError
from ..helpers.memory import Memory
from ..helpers.optional import import_dependency
from .base import BaseGoogle


class GoogleGemini(BaseGoogle):
    """Google Gemini LLM
    BaseGoogle class is extended for Google Gemini model. The default and only model
    support at the moment is models/gemini-pro.

    """

    model: str = "models/gemini-pro"
    google_gemini: Any

    def __init__(self, api_key: str, **kwargs):
        """
        __init__ method of GoogleGemini Class
        Args:
            api_key (str): API Key
            **kwargs: Extended Parameters inferred from BaseGoogle Class
        """
        self._configure(api_key=api_key)
        self._set_params(**kwargs)

    def _configure(self, api_key: str):
        """
        Configure Google Gemini API Key
        Args:
            api_key (str): A string of API keys generated from Google Cloud.

        Returns:
            None.
        """

        if not api_key:
            raise APIKeyNotFoundError("Google Gemini API key is required")

        err_msg = "Install google-generativeai >= 0.3 for Google Gemini API"
        self.google_gemini = import_dependency("google.generativeai", extra=err_msg)

        self.google_gemini.configure(api_key=api_key)
        final_model = self.google_gemini.GenerativeModel(self.model)
        self.google_gemini = final_model

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

    def _generate_text(self, prompt: str, memory: Optional[Memory] = None) -> str:
        """
        Generates text for prompt.

        Args:
            prompt (str): A string representation of the prompt.

        Returns:
            str: LLM response.

        """
        self._validate()
        updated_prompt = self.prepend_system_prompt(prompt, memory)

        self.last_prompt = updated_prompt
        completion = self.google.GoogleGemini.generate_content(
            contents=prompt,
            temperature=self.temperature,
            top_p=self.top_p,
            top_k=self.top_k,
            max_output_tokens=self.max_output_tokens,
        )

        return completion.text

    @property
    def type(self) -> str:
        return "google-gemini"
