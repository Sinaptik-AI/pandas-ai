import logging
import traceback
from typing import Any, List
from ...helpers.code_manager import CodeExecutionContext
from ...helpers.logger import Logger
from ..base_logic_unit import BaseLogicUnit
from ..pipeline_context import PipelineContext
from ...prompts.correct_error_prompt import CorrectErrorPrompt


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
        pipeline_context: PipelineContext = kwargs.get("context")
        logger: Logger = kwargs.get("logger")

        code = input
        retry_count = 0
        code_to_run = code
        result = None
        while retry_count < pipeline_context.config.max_retries:
            try:
                # Execute the code
                code_context = CodeExecutionContext(
                    pipeline_context.get_intermediate_value("last_prompt_id"),
                    pipeline_context.get_intermediate_value("skills"),
                )

                result = pipeline_context.query_exec_tracker.execute_func(
                    pipeline_context.get_intermediate_value(
                        "code_manager"
                    ).execute_code,
                    code=code_to_run,
                    context=code_context,
                )

                break

            except Exception as e:
                if (
                    not pipeline_context.config.use_error_correction_framework
                    or retry_count >= pipeline_context.config.max_retries - 1
                ):
                    raise e

                retry_count += 1

                logger.log(
                    f"Failed to execute code with a correction framework "
                    f"[retry number: {retry_count}]",
                    level=logging.WARNING,
                )

                traceback_error = traceback.format_exc()
                code_to_run = pipeline_context.query_exec_tracker.execute_func(
                    self._retry_run_code,
                    code,
                    pipeline_context,
                    logger,
                    traceback_error,
                )

        return result

    def _retry_run_code(
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
            "engine": context.dfs[0].engine,
            "code": code,
            "error_returned": e,
            "output_type_hint": context.get_intermediate_value(
                "output_type_helper"
            ).template_hint,
        }
        error_correcting_instruction = context.get_intermediate_value("get_prompt")(
            "correct_error",
            default_prompt=CorrectErrorPrompt(),
            default_values=default_values,
        )

        return context.config.llm.generate_code(error_correcting_instruction)
