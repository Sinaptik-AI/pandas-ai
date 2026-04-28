from __future__ import annotations

from typing import TYPE_CHECKING

from openai import OpenAI

from pandasai.core.prompts.base import BasePrompt
from pandasai.llm.base import LLM

if TYPE_CHECKING:
    from pandasai.agent.state import AgentState


class LocalLLM(LLM):
    """LLM wrapper for OpenAI-compatible local servers (Ollama, LM Studio, etc.).

    Connects to any server that exposes an OpenAI-compatible ``/v1`` endpoint,
    such as `Ollama <https://ollama.com/>`_ or
    `LM Studio <https://lmstudio.ai/>`_.

    Args:
        api_base (str): Base URL of the local server, e.g.
            ``"http://localhost:11434/v1"`` for Ollama.
        model (str): Model name to request from the server.
        api_key (str): API key.  Most local servers accept any non-empty
            string; defaults to ``"dummy"`` when omitted.
        **kwargs: Extra keyword arguments forwarded to every
            ``chat.completions.create`` call (e.g. ``temperature``,
            ``max_tokens``).

    Example::

        from pandasai.llm.local_llm import LocalLLM

        # Ollama
        ollama_llm = LocalLLM(api_base="http://localhost:11434/v1", model="codellama")

        # LM Studio
        lm_studio_llm = LocalLLM(api_base="http://localhost:1234/v1")
    """

    def __init__(
        self, api_base: str, model: str = "", api_key: str = "", **kwargs
    ) -> None:
        if not api_key:
            api_key = "dummy"
        super().__init__(api_key=api_key)
        self.model = model
        self._client = OpenAI(base_url=api_base, api_key=api_key).chat.completions
        self._invocation_params = kwargs

    @property
    def type(self) -> str:
        return "local"

    def call(self, instruction: BasePrompt, context: AgentState = None) -> str:
        memory = context.memory if context else None
        self.last_prompt = self.prepend_system_prompt(instruction.to_string(), memory)

        response = self._client.create(
            model=self.model,
            messages=[{"role": "user", "content": self.last_prompt}],
            **self._invocation_params,
        )
        return response.choices[0].message.content
