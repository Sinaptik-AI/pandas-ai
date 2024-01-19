from typing import Any, Callable
from pandasai.exceptions import InvalidLLMOutputType
from pandasai.helpers.logger import Logger
from pandasai.pipelines.base_logic_unit import BaseLogicUnit
from pandasai.pipelines.pipeline_context import PipelineContext
from pandasai.pipelines.smart_datalake_chat.error_correction_pipeline.error_correction_pipeline_input import (
    ErrorCorrectionPipelineInput,
)
from pandasai.pipelines.logic_unit_output import LogicUnitOutput
from pandasai.prompts.base import AbstractPrompt
from pandasai.prompts.correct_error_prompt import CorrectErrorPrompt
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

        default_values = {
            "code": input.code,
            "error_returned": e,
            "output_type_hint": self.context.get("output_type_helper").template_hint,
        }
        error_correcting_instruction = self.get_prompt(
            e,
            default_values,
        )
        if self.on_prompt_generation:
            self.on_prompt_generation(error_correcting_instruction)

        print(error_correcting_instruction)

        return LogicUnitOutput(
            error_correcting_instruction,
            True,
            "Prompt Generated Successfully",
            {"generated_prompt": error_correcting_instruction.to_string()},
        )

    def _get_error_prompt(self, e: Exception) -> AbstractPrompt:
        if isinstance(e, InvalidLLMOutputType):
            return CorrectOutputTypeErrorPrompt()
        else:
            return CorrectErrorPrompt()

    def get_prompt(self, e: Exception, default_values: dict) -> AbstractPrompt:
        """
        Return a prompt by key.

        Args:
            values (dict): The values to use for the prompt

        Returns:
            AbstractPrompt: The prompt
        """
        prompt = self._get_error_prompt(e)

        # Set default values for the prompt
        prompt.set_config(self.context.config)

        # Set the variables for the prompt
        values = {
            "dfs": self.context.dfs,
            "conversation": self.context.memory.get_conversation(),
            "prev_conversation": self.context.memory.get_previous_conversation(),
            "last_message": self.context.memory.get_last_message(),
            "skills": self.context.skills_manager.prompt_display() or "",
        }
        values |= default_values
        prompt.set_vars(values)

        self.logger.log(f"Using prompt: {prompt}")
        return prompt
