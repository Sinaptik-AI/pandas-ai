"""Fake LLM"""

from typing import Optional

from ..prompts.base import Prompt
from .base import LLM


class FakeLLM(LLM):
    """Fake LLM"""

    _output: str = 'print("Hello world")'

    def __init__(self, output: Optional[str] = None):
        if output is not None:
            self._output = output

    def call(self, instruction: Prompt, value: str, suffix: str = "") -> str:
        self.last_prompt = str(instruction) + str(value) + suffix
        return self._output

    @property
    def type(self) -> str:
        return "fake"
