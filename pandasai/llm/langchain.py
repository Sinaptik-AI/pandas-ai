from pandasai.prompts.base import Prompt
from .base import LLM


class LangchainLLM(LLM):
    """
    Class to wrap Langchain LLMs and make PandasAI interoperable
    with LangChain.
    """

    _langchain_llm = None

    def __init__(self, langchain_llm):
        try:
            from langchain.llms.base import BaseLLM

            if not isinstance(langchain_llm, BaseLLM):
                raise TypeError(
                    "LangchainLLM must be initialized with a Langchain LLM."
                )

            self._langchain_llm = langchain_llm
        except ImportError:
            raise ImportError(
                "Langchain is not installed. Please install it using "
                "`pip install pandasai[langchain]` or `poetry install "
                "pandasai[langchain]`."
            )

    def call(self, instruction: Prompt, suffix: str = "") -> str:
        prompt = instruction.to_string() + suffix
        return self._langchain_llm.predict(prompt)

    @property
    def type(self) -> str:
        return "langchain_" + self._langchain_llm._llm_type
