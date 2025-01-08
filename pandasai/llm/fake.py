"""Fake LLM"""

from typing import Optional

from pandasai.agent.state import AgentState
from pandasai.core.prompts.base import BasePrompt

from .base import LLM


class FakeLLM(LLM):
    """Fake LLM"""

    _output: str = """result = { 'type': 'string', 'value': "Hello World" }"""
    _type: str = "fake"

    def __init__(self, output: Optional[str] = None, type: str = "fake"):
        if output is not None:
            self._output = output
        self._type = type
        self.called = False
        self.last_prompt = None
        self.response = "Mocked response"

    def call(self, instruction: BasePrompt, context: AgentState = None) -> str:
        self.called = True
        self.last_prompt = instruction.to_string()
        return self.response

    @property
    def type(self) -> str:
        return self._type
