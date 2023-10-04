"""Gpt4free LLM

This module is to run the OpenAI API using gpt4free (reverse engineering).

Example:
    Use below example to call Gpt4free Model

    >>> from pandasai.llm.gpt4free import Gpt4free
"""

import g4f

from pandasai.prompts.base import AbstractPrompt

from .base import LLM


class Gpt4free(LLM):
    """
    Class to wrap gpt4free LLMs and make PandasAI interoperable
    with gpt4free.
    """

    def __init__(
        self,
        model: str = "gpt-3.5-turbo",
        provider: g4f.Provider = None,
        stream: bool = False,
    ):
        """
        __init__ method of Gpt4free Class

        Args:
            model (str): Model of OpenAI API.
            provider (g4f.Provider): The Provider of OpenAI API.
            stream (bool): Completion with streaming.

        """
        self.model = model
        self.provider = provider
        self.stream = stream

    def call(self, instruction: AbstractPrompt, suffix: str = "") -> str:
        prompt = instruction.to_string() + suffix

        try:
            response = g4f.ChatCompletion.create(
                model=self.model,
                provider=self.provider,
                messages=[{"role": "user", "content": prompt}],
            )
        except Exception as e:
            raise RuntimeError(f"Failed to create chat completion with Gpt4free: {str(e)}") from e
        return response

    @property
    def type(self) -> str:
        return "gpt4free"
