from __future__ import annotations

from typing import TYPE_CHECKING, Union

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.language_models.llms import BaseLLM

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


class LangchainLLM(LLM):
    """
    Class to wrap Langchain LLMs and make PandasAI interoperable
    with LangChain.
    """

    langchain_llm = None

    def __init__(self, langchain_llm: Union[BaseLLM, BaseChatModel]):
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

    @staticmethod
    def is_langchain_llm(llm: LLM) -> bool:
        return hasattr(llm, "_llm_type")

    @property
    def type(self) -> str:
        return f"langchain_{self.langchain_llm._llm_type}"
