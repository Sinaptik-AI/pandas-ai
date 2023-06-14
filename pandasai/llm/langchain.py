""" Langchain LLMs

This module is meant to be a wrapper around Langchain LLMs to enable the
support of multiple LLMs and make PandasAI interoperable with LangChain.
"""

from pandasai.prompts.base import Prompt
from .base import LLM

from langchain.llms.base import LLM as LangchainBaseLLM


class LangchainLLM(LLM):
    """
    Class to wrap Langchain LLMs and make PandasAI interoperable
    with LangChain.
    """

    _langchain_llm: LangchainBaseLLM = None

    def __init__(self, langchain_llm: LangchainBaseLLM):
        self._langchain_llm = langchain_llm

    def call(self, instruction: Prompt, value: str, suffix: str = "") -> str:
        prompt = str(instruction) + value + suffix
        return self._langchain_llm(prompt)

    @property
    def type(self) -> str:
        return "langchain_" + self._langchain_llm._llm_type
