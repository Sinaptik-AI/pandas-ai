from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Optional

from pandasai.helpers.memory import Memory

from pandasai.exceptions import (
    MethodNotImplementedError,
)
from pandasai.prompts.base import BasePrompt
from pandasai.llm.base import LLM

if TYPE_CHECKING:
    from pandasai.pipelines.pipeline_context import PipelineContext



class BaseGoogle(LLM):
    """Base class to implement a new Google LLM

    LLM base class is extended to be used with
    """

    temperature: Optional[float] = 0
    top_p: Optional[float] = 0.8
    top_k: Optional[int] = 40
    max_output_tokens: Optional[int] = 1000

    def _valid_params(self):
        return ["temperature", "top_p", "top_k", "max_output_tokens"]

    def _set_params(self, **kwargs):
        """
        Dynamically set Parameters for the object.

        Args:
            **kwargs:
                Possible keyword arguments: "temperature", "top_p", "top_k",
                "max_output_tokens".

        Returns:
            None.

        """

        valid_params = self._valid_params()
        for key, value in kwargs.items():
            if key in valid_params:
                setattr(self, key, value)

    def _validate(self):
        """Validates the parameters for Google"""

        if self.temperature is not None and not 0 <= self.temperature <= 1:
            raise ValueError("temperature must be in the range [0.0, 1.0]")

        if self.top_p is not None and not 0 <= self.top_p <= 1:
            raise ValueError("top_p must be in the range [0.0, 1.0]")

        if self.top_k is not None and not 0 <= self.top_k <= 100:
            raise ValueError("top_k must be in the range [0.0, 100.0]")

        if self.max_output_tokens is not None and self.max_output_tokens <= 0:
            raise ValueError("max_output_tokens must be greater than zero")

    @abstractmethod
    def _generate_text(self, prompt: str, memory: Optional[Memory] = None) -> str:
        """
        Generates text for prompt, specific to implementation.

        Args:
            prompt (str): A string representation of the prompt.

        Returns:
            str: LLM response.

        """
        raise MethodNotImplementedError("method has not been implemented")

    def call(self, instruction: BasePrompt, context: PipelineContext = None) -> str:
        """
        Call the Google LLM.

        Args:
            instruction (BasePrompt): Instruction to pass.
            context (PipelineContext): Pass PipelineContext.

        Returns:
            str: LLM response.

        """
        self.last_prompt = instruction.to_string()
        memory = context.memory if context else None
        return self._generate_text(self.last_prompt, memory)
