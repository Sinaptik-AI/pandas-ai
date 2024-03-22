from typing import Optional

from ..helpers.request import Session
from ..prompts.base import BasePrompt
from .base import LLM


class BambooLLM(LLM):
    _session: Session

    def __init__(
        self, endpoint_url: Optional[str] = None, api_key: Optional[str] = None
    ):
        self._session = Session(endpoint_url=endpoint_url, api_key=api_key)

    def call(self, instruction: BasePrompt, _context=None) -> str:
        data = instruction.to_json()
        response = self._session.post("/llm/chat", json=data)
        return response["data"]

    @property
    def type(self) -> str:
        return "bamboo_llm"
