from typing import Any, Callable

from pandasai.exceptions import ExecuteSQLQueryNotUsed, InvalidLLMOutputType
from pandasai.helpers.logger import Logger
from pandasai.pipelines.base_logic_unit import BaseLogicUnit
from pandasai.pipelines.chat.error_correction_pipeline.error_correction_pipeline_input import (
    ErrorCorrectionPipelineInput,
)
from pandasai.pipelines.logic_unit_output import LogicUnitOutput
from pandasai.pipelines.pipeline_context import PipelineContext
from pandasai.prompts.base import BasePrompt
from pandasai.prompts.correct_error_prompt import CorrectErrorPrompt
from pandasai.prompts.correct_execute_sql_query_usage_error_prompt import (
    CorrectExecuteSQLQueryUsageErrorPrompt,
)
from pandasai.prompts.correct_output_type_error_prompt import (
    CorrectOutputTypeErrorPrompt,
)


class ErrorPromptGeneration(BaseLogicUnit):
    on_prompt_generation: Callable[[str], None]

    def __init__(
        self,
        on_prompt_generation=None,
        skip_if=None,
        on_execution=None,
        before_execution=None,
    ):
        self.on_prompt_generation = on_prompt_generation
        super().__init__(skip_if, on_execution, before_execution)

    def execute(self, input: ErrorCorrectionPipelineInput, **kwargs) -> Any:
        """
        A method to retry the code execution with error correction framework.

        Args:
            code (str): A python code
            context (PipelineContext) : Pipeline Context
            logger (Logger) : Logger
            e (Exception): An exception
            dataframes

        Returns (str): A python code
        """
        self.context: PipelineContext = kwargs.get("context")
        self.logger: Logger = kwargs.get("logger")
        e = input.exception

        prompt = self.get_prompt(e, input.code)
        if self.on_prompt_generation:
            self.on_prompt_generation(prompt)

        self.logger.log(f"Using prompt: {prompt}")

        return LogicUnitOutput(
            prompt,
            True,
            "Prompt Generated Successfully",
            {
                "content_type": "prompt",
                "value": prompt.to_string(),
            },
        )

    def get_prompt(self, e: Exception, code: str) -> BasePrompt:
        """
        Return a prompt by key.

        Args:
            values (dict): The values to use for the prompt

        Returns:
            BasePrompt: The prompt
        """
        return (
            CorrectOutputTypeErrorPrompt(
                context=self.context,
                code=code,
                error=e,
                output_type=self.context.get("output_type"),
            )
            if isinstance(e, InvalidLLMOutputType)
            else CorrectExecuteSQLQueryUsageErrorPrompt(
                context=self.context, code=code, error=e
            )
            if isinstance(e, ExecuteSQLQueryNotUsed)
            else CorrectErrorPrompt(
                context=self.context,
                code=code,
                error=e,
            )
        )
