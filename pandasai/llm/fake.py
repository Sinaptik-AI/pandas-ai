"""Fake LLM"""

from .base import LLM


class FakeLLM(LLM):
    """Fake LLM"""

    output: str = 'print("Hello world")'

    def __init__(self, output: str = None):
        self.output = output or self.output

    def call(self, instruction: str, value: str) -> str:
        return self.output

    @property
    def type(self) -> str:
        return "fake"
