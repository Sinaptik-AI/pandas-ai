import logging
import traceback
from typing import Any, List
from pandasai.helpers.code_manager import CodeExecutionContext
from pandasai.helpers.logger import Logger
from pandasai.pipelines.base_logic_unit import BaseLogicUnit
from pandasai.pipelines.pipeline_context import PipelineContext
from pandasai.prompts.correct_error_prompt import CorrectErrorPrompt


class CodeExecution(BaseLogicUnit):

    """
    Code Execution Stage
    """

    pass

    def execute(self, input: Any, **kwargs) -> Any:
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
                result = pipeline_context.get_intermediate_value(
                    "code_manager"
                ).execute_code(
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
                [
                    code_to_run,
                    reasoning,
                    answer,
                ] = pipeline_context.query_exec_tracker.execute_func(
                    self._retry_run_code,
                    code,
                    pipeline_context,
                    logger,
                    traceback_error,
                )

                pipeline_context.add_intermediate_value("reasoning", reasoning)
                pipeline_context.add_intermediate_value("answer", answer)

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
        }
        error_correcting_instruction = context.get_intermediate_value("get_prompt")(
            "correct_error",
            default_prompt=CorrectErrorPrompt,
            default_values=default_values,
        )

        result = context.config.llm.generate_code(error_correcting_instruction)
        if context.config.callback is not None:
            context.config.callback.on_code(result[0])

        return result
