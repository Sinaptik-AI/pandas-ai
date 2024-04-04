from __future__ import annotations

from typing import TYPE_CHECKING

from openai import OpenAI

from ..helpers.memory import Memory
from ..prompts.base import BasePrompt
from .base import LLM

if TYPE_CHECKING:
    from pandasai.pipelines.pipeline_context import PipelineContext


class LocalLLM(LLM):
    def __init__(self, api_base: str, model: str = "", api_key: str = "", **kwargs):
        if not api_key:
            api_key = "dummy"

        self.model = model
        self.client = OpenAI(base_url=api_base, api_key=api_key).chat.completions
        self._invocation_params = kwargs

    def chat_completion(self, value: str, memory: Memory) -> str:
        messages = memory.to_openai_messages() if memory else []

        # adding current prompt as latest query message
        messages.append(
            {
                "role": "user",
                "content": value,
            }
        )

        params = {"model": self.model, "messages": messages, **self._invocation_params}
        response = self.client.create(**params)

        return response.choices[0].message.content

    def call(self, instruction: BasePrompt, context: PipelineContext = None) -> str:
        self.last_prompt = instruction.to_string()

        memory = context.memory if context else None

        return self.chat_completion(self.last_prompt, memory)

    @property
    def type(self) -> str:
        return "local"
