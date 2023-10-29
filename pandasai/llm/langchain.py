from pandasai.prompts.base import AbstractPrompt
from .base import LLM


class LangchainLLM(LLM):
    """
    Class to wrap Langchain LLMs and make PandasAI interoperable
    with LangChain.
    """

    _langchain_llm = None

    def __init__(self, langchain_llm):
        self._langchain_llm = langchain_llm

    def call(self, instruction: AbstractPrompt, suffix: str = "") -> str:
        prompt = instruction.to_string() + suffix
        return self._langchain_llm.predict(prompt)

    @property
    def type(self) -> str:
        return f"langchain_{self._langchain_llm._llm_type}"
