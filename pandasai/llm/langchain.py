from pandasai.prompts.base import Prompt
from .base import LLM


class LangchainLLM(LLM):
    """
    Class to wrap Langchain LLMs and make PandasAI interoperable
    with LangChain.
    """

    _langchain_llm = None

    def __init__(self, langchain_llm):
        self._langchain_llm = langchain_llm

    def call(self, instruction: Prompt, value: str, suffix: str = "") -> str:
        prompt = str(instruction) + value + suffix
        return self._langchain_llm.predict(prompt)

    @property
    def type(self) -> str:
        return "langchain_" + self._langchain_llm._llm_type
