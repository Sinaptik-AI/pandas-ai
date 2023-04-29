from .base import LLM


class FakeLLM(LLM):
    output: str = 'print("Hello world")'

    def __init__(self, output: str = None):
        self.output = output or self.output

    def call(self, instruction: str, input: str) -> str:
        return self.output

    @property
    def _type(self) -> str:
        return "fake"
