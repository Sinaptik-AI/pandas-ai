from typing import Any
from pandasai.exceptions import LLMNotFoundError
from pandasai.pipelines.base_logic_unit import BaseLogicUnit
from pandasai.prompts.file_based_prompt import FileBasedPrompt


class PromptExecution(BaseLogicUnit):
    def execute(self, input: FileBasedPrompt, **kwargs) -> Any:
        config = kwargs["config"]
        if config.llm is None:
            raise LLMNotFoundError()

        llm = config.llm

        return llm.call(input)
