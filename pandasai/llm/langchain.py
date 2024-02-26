from typing import Union

from pandasai.prompts.base import AbstractPrompt

from .base import LLM
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.language_models.llms import BaseLLM

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

    def __init__(self, langchain_llm: Union[BaseLLM, BaseChatModel]):
        self._langchain_llm = langchain_llm

    def call(self, instruction: AbstractPrompt, suffix: str = "") -> str:
        prompt = instruction.to_string() + suffix
        res = self._langchain_llm.invoke(prompt)
        if isinstance(self._langchain_llm, BaseChatModel):
            return res.content

        return res

    @property
    def type(self) -> str:
        return f"langchain_{self._langchain_llm._llm_type}"
