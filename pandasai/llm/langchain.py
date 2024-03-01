from __future__ import annotations

try:
    from langchain_core.language_models import BaseLanguageModel
    from langchain_core.language_models.chat_models import BaseChatModel

except ImportError:
    from unittest.mock import Mock

    # Fallback definitions if langchain_core is not installed
    BaseLanguageModel = BaseChatModel = Mock

from typing import TYPE_CHECKING

from pandasai.prompts.base import BasePrompt

from .base import LLM

if TYPE_CHECKING:
    from pandasai.pipelines.pipeline_context import PipelineContext

"""Langchain LLM 

This module is to run LLM using LangChain framework.

Example:
    Use below example to call LLM
    >>> from pandasai.llm.langchain import LangchainLLm
"""


def is_langchain_llm(llm) -> bool:
    return isinstance(llm, BaseLanguageModel)


class LangchainLLM(LLM):
    """
    Class to wrap Langchain LLMs and make PandasAI interoperable
    with LangChain.
    """

    langchain_llm: BaseLanguageModel

    def __init__(self, langchain_llm: BaseLanguageModel):
        self.langchain_llm = langchain_llm

    def call(
        self, instruction: BasePrompt, context: PipelineContext = None, suffix: str = ""
    ) -> str:
        prompt = instruction.to_string() + suffix
        memory = context.memory if context else None
        prompt = self.prepend_system_prompt(prompt, memory)
        self.last_prompt = prompt

        res = self.langchain_llm.invoke(prompt)
        return res.content if isinstance(self.langchain_llm, BaseChatModel) else res

    @property
    def type(self) -> str:
        return f"langchain_{self.langchain_llm._llm_type}"
