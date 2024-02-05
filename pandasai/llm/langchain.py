from pandasai.helpers.memory import Memory
from pandasai.prompts.base import BasePrompt
from .base import LLM

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

    def __init__(self, langchain_llm):
        self.langchain_llm = langchain_llm

    def call(self, instruction: BasePrompt, memory: Memory = None) -> str:
        prompt = instruction.to_string()
        prompt = (
            memory.get_system_prompt() + "\n" + prompt
            if memory and memory.agent_info
            else prompt
        )
        return self.langchain_llm.predict(prompt)

    @staticmethod
    def is_langchain_llm(llm: LLM) -> bool:
        return hasattr(llm, "_llm_type")

    @property
    def type(self) -> str:
        return f"langchain_{self.langchain_llm._llm_type}"
