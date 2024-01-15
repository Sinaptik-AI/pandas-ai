import logging
import traceback
from typing import Any, Callable, List

from pandasai.pipelines.step_output import StepOutput
from pandasai.responses.response_serializer import ResponseSerializer
from ...helpers.code_manager import CodeExecutionContext, CodeManager
from ...helpers.logger import Logger
from ..base_logic_unit import BaseLogicUnit
from ..pipeline_context import PipelineContext


class CodeExecution(BaseLogicUnit):
    """
    Code Execution Stage
    """

    def __init__(self, on_failure: Callable[[str, Exception], None] = None, **kwargs):
        super().__init__()
        self.on_failure = on_failure

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
            self.context.get("last_prompt_id"), self.context.skills_manager
        )

        code_manager = CodeManager(
            dfs=self.context.dfs,
            config=self.context.config,
            logger=self.logger,
        )

        # code = input.input
        retry_count = 0
        code_to_run = input
        result = None
        while retry_count < self.context.config.max_retries:
            try:
                result = code_manager.execute_code(code_to_run, code_context)
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
                # TODO - Move this implement to main execute function
                # Temporarily done for test cases this is to be fixed move to the main function
                code_to_run = self.retry_run_code(
                    code_to_run, self.context, self.logger, traceback_error
                )

        return StepOutput(
            result,
            True,
            "Code Executed Successfully",
            {"result": ResponseSerializer.serialize(result)},
        )

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
        if self.on_failure:
            return self.on_failure(code, e)
        else:
            raise e
