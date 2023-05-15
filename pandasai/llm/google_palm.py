"""Google Palm LLM"""
from typing import Optional

from google import generativeai

from ..exceptions import APIKeyNotFoundError
from .base import LLM


class GooglePalm(LLM):
    """Google Palm LLM"""

    model: str = "models/text-bison-001"
    temperature: Optional[float] = 0
    top_p: Optional[float] = None
    top_k: Optional[float] = None
    max_output_tokens: Optional[int] = None

    def __init__(self, api_key: str, **kwargs):
        if not api_key:
            raise APIKeyNotFoundError("Google Palm API key is required")

        generativeai.configure(api_key=api_key)
        self._set_params(**kwargs)

    def _set_params(self, **kwargs):
        valid_params = ["model", "temperature", "top_p", "top_k", "max_output_tokens"]
        for key, value in kwargs.items():
            if key in valid_params:
                setattr(self, key, value)

    def _validate(self):
        """Validates the parameters for Google Palm"""
        if self.temperature is not None and not 0 <= self.temperature <= 1:
            raise ValueError("temperature must be in the range [0.0, 1.0]")

        if self.top_p is not None and not 0 <= self.top_p <= 1:
            raise ValueError("top_p must be in the range [0.0, 1.0]")

        if self.top_k is not None and not 0 <= self.top_k <= 1:
            raise ValueError("top_k must be in the range [0.0, 1.0]")

        if self.max_output_tokens is not None and self.max_output_tokens <= 0:
            raise ValueError("max_output_tokens must be greater than zero")

    def _generate_text(self, prompt: str) -> str:
        """
        Generates text for prompt

        Args:
            prompt (str): Prompt

        Returns:
            str: LLM response
        """
        self._validate()
        completion = generativeai.generate_text(
            model=self.model,
            prompt=prompt,
            temperature=self.temperature,
            top_p=self.top_p,
            top_k=self.top_k,
            max_output_tokens=self.max_output_tokens,
        )
        return completion.result

    def call(self, instruction: str, value: str, suffix: str = "") -> str:
        """
        Call the Google Palm LLM.

        Args:
            instruction (str): Instruction to pass
            value (str): Value to pass
            suffix (str): Suffix to pass

        Returns:
            str: Response
        """
        self.last_prompt = str(instruction) + str(value)
        prompt = str(instruction) + str(value) + suffix
        return self._generate_text(prompt)

    @property
    def type(self) -> str:
        return "google-palm"
