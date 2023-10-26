"""Anthropic's Claude LLM

This module is to run the Claude API and maintained by Anthropic.
To read more on Anthropic Calude follow
https://docs.anthropic.com/claude/reference/getting-started-with-the-api

Example:
    Use below example to call AnthropicClaude Model

    >>> from pandasai.llm.anthropic import AnthropicClaude
"""
from typing import Any
from .base import BaseAnthropic
from ..helpers.optional import import_dependency
from ..exceptions import APIKeyNotFoundError


class Anthropic(BaseAnthropic):
    """
    Anthropic's Claude LLM
    BaseAnthropic is extended for Anthropic's Claude model.
    """

    model: str = "claude-2"
    anthropic_claude: Any

    def __init__(self, api_key, **kwargs) -> None:
        """
        __init__ method of Anthropic Class
        Args:
            api_key (str) : API Key
            **kwargs: Extended Parameters inferred from BaseAnthropic Class.
        """
        self._configure(api_key=api_key)
        self._set_params(**kwargs)

    def _configure(self, api_key: str):
        """
        Configure Anthropic Claude API Key
        Args:
            api_key (str):A string of API keys generated from Anthropic dashboard.

        Return:
            None.
        """
        if not api_key:
            raise APIKeyNotFoundError("Anthropic API key is required")

        err_msg = "Install anthropic >=0.5 for Anthropics API"
        anthropic = import_dependency("anthropic", err_msg)
        ### Configure api key

        self.anthropic_claude = anthropic.Anthropic(api_key=api_key)

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
        completion = self.anthropic_claude.completions.create(
            model=self.model,
            prompt=prompt,
            temperature=self.temperature,
            top_p=self.top_p,
            top_k=self.top_k,
            max_tokens_to_sample=self.max_output_tokens,
        )
        return completion.completion

    @property
    def type(self) -> str:
        return "anthropic"
