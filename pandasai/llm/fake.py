"""Fake LLM"""

from typing import Optional

from ..prompts.base import AbstractPrompt
from .base import LLM


class FakeLLM(LLM):
    """Fake LLM"""

    _output: str = """def analyze_data(dfs):
    return { 'type': 'text', 'value': "Hello World" }"""

    def __init__(self, output: Optional[str] = None):
        if output is not None:
            self._output = output

    def call(self, instruction: AbstractPrompt, suffix: str = "") -> str:
        self.last_prompt = instruction.to_string() + suffix
        return self._output

    @property
    def type(self) -> str:
        return "fake"
