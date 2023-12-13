import logging
import traceback
from typing import Any, List
from ...helpers.code_manager import CodeExecutionContext, CodeManager
from ...helpers.logger import Logger
from ..base_logic_unit import BaseLogicUnit
from ..pipeline_context import PipelineContext
from ...prompts.correct_error_prompt import CorrectErrorPrompt
from ...prompts.base import AbstractPrompt


class CodeExecution(BaseLogicUnit):
    """
    Code Execution Stage
    """

    pass

    def execute(self, input: Any, **kwargs) -> Any:
        """
        This method will return output according to
        Implementation.

        :param input: Your input data.
        :param kwargs: A dictionary of keyword arguments.
            - 'logger' (any): The logger for logging.
            - 'config' (Config): Global configurations for the test
            - 'context' (any): The execution context.

        :return: The result of the execution.
        """
        self.context: PipelineContext = kwargs.get("context")
        self.logger: Logger = kwargs.get("logger")

        # Execute the code
        code_context = CodeExecutionContext(
            self.context.get("last_prompt_id"), self.context.skills
        )

        code_manager = CodeManager(
            dfs=self.context.dfs,
            config=self.context.config,
            logger=self.logger,
        )

        code = input
        retry_count = 0
        code_to_run = code
        result = None
        while retry_count < self.context.config.max_retries:
            try:
                result = self.context.query_exec_tracker.execute_func(
                    code_manager.execute_code,
                    code=code_to_run,
                    context=code_context,
                )

                break

            except Exception as e:
                if (
                    not self.context.config.use_error_correction_framework
                    or retry_count >= self.context.config.max_retries - 1
                ):
                    raise e

                retry_count += 1

                self.logger.log(
                    f"Failed to execute code with a correction framework "
                    f"[retry number: {retry_count}]",
                    level=logging.WARNING,
                )

                traceback_error = traceback.format_exc()
                code_to_run = self.context.query_exec_tracker.execute_func(
                    self.retry_run_code,
                    code,
                    self.context,
                    self.logger,
                    traceback_error,
                )

        return result

    def retry_run_code(
        self, code: str, context: PipelineContext, logger: Logger, e: Exception
    ) -> List:
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

        logger.log(f"Failed with error: {e}. Retrying", logging.ERROR)

        default_values = {
            "code": code,
            "error_returned": e,
            "output_type_hint": context.get("output_type_helper").template_hint,
        }
        error_correcting_instruction = self.get_prompt(
            default_values,
        )

        return context.config.llm.generate_code(error_correcting_instruction)

    def get_prompt(self, default_values) -> AbstractPrompt:
        """
        Return a prompt by key.

        Args:
            values (dict): The values to use for the prompt

        Returns:
            AbstractPrompt: The prompt
        """
        prompt = (
            self.context.config.custom_prompts.get("correct_error")
            or CorrectErrorPrompt()
        )

        # Set default values for the prompt
        prompt.set_config(self.context.config)

        # Set the variables for the prompt
        values = {
            "dfs": self.context.dfs,
            "conversation": self.context.memory.get_conversation(),
            "prev_conversation": self.context.memory.get_previous_conversation(),
            "last_message": self.context.memory.get_last_message(),
            "skills": self.context.skills.prompt_display() or "",
        }
        values |= default_values
        prompt.set_vars(values)

        self.logger.log(f"Using prompt: {prompt}")
        return prompt
