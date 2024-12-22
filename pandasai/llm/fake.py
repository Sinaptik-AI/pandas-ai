"""Fake LLM"""

from typing import Optional

from pandasai.pipelines.pipeline_context import PipelineContext

from ..prompts.base import BasePrompt
from .base import LLM


class FakeLLM(LLM):
    """Fake LLM"""

    _output: str = """result = { 'type': 'string', 'value': "Hello World" }"""

    def __init__(self, output: Optional[str] = None):
        if output is not None:
            self._output = output

    def call(self, instruction: BasePrompt, context: PipelineContext = None) -> str:
        self.last_prompt = instruction.to_string()
        return self._output

    def get_output(self) -> str:
        return self._output

    def set_output(self, output: str):
        self._output = output

    @property
    def type(self) -> str:
        return "fake"
