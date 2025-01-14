from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from pandasai.core.prompts.base import BasePrompt

from pandasai.helpers.session import Session
from pandasai.llm.base import LLM


class BambooLLM(LLM):
    _session: Session

    def __init__(
        self, endpoint_url: Optional[str] = None, api_key: Optional[str] = None
    ):
        self._session = Session(endpoint_url=endpoint_url, api_key=api_key)

    def call(self, instruction: BasePrompt, _context=None) -> str:
        response = self._session.post(
            "/query", json={"prompt": instruction.to_string()}
        )
        return response["answer"]

    @property
    def type(self) -> str:
        return "bamboo_llm"
