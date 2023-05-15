from typing import Optional

from google import generativeai

from ..exceptions import APIKeyNotFoundError
from .base import LLM


class GooglePalm(LLM):
    def __init__(
        self,
        api_key: str,
        model_name: str = "models/text-bison-001",
        temperature: Optional[float] = 0,
        top_p: Optional[float] = None,
        top_k: Optional[float] = None,
        max_output_tokens: Optional[int] = None,
    ):
        if not api_key:
            raise APIKeyNotFoundError("Google Palm API key is required")

        generativeai.configure(api_key=api_key)

        self.model_name = model_name

        if temperature is not None and not 0 <= temperature <= 1:
            raise ValueError("temperature must be in the range [0.0, 1.0]")
        self.temperature = temperature

        if top_p is not None and not 0 <= top_p <= 1:
            raise ValueError("top_p must be in the range [0.0, 1.0]")
        self.top_p = top_p

        if top_k is not None and not 0 <= top_k <= 1:
            raise ValueError("top_k must be in the range [0.0, 1.0]")
        self.top_k = top_k

        if max_output_tokens is not None and max_output_tokens <= 0:
            raise ValueError("max_output_tokens must be greater than zero")
        self.max_output_tokens = max_output_tokens

    def _generate_text(self, prompt: str) -> str:
        """
        Generates text for prompt

        Args:
            prompt (str): Prompt

        Returns:
            str: LLM response
        """
        completion = generativeai.generate_text(
            model=self.model_name,
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
