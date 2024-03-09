import logging
import traceback
from typing import Any, Callable

from pandasai.exceptions import InvalidLLMOutputType
from pandasai.pipelines.logic_unit_output import LogicUnitOutput
from pandasai.responses.response_serializer import ResponseSerializer

from ...helpers.code_manager import CodeExecutionContext, CodeManager
from ...helpers.logger import Logger
from ...helpers.output_validator import OutputValidator
from ..base_logic_unit import BaseLogicUnit
from ..pipeline_context import PipelineContext


class CodeExecution(BaseLogicUnit):
    """
    Code Execution Stage
    """

    def __init__(
        self,
        on_failure: Callable[[str, Exception], None] = None,
        on_retry: Callable[[str, Exception], None] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.on_failure = on_failure
        self.on_retry = on_retry

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
        while retry_count <= self.context.config.max_retries:
            try:
                result = code_manager.execute_code(code_to_run, code_context)

                if self.context.get("output_type") != "" and (
                    output_helper := self.context.get("output_type")
                ):
                    (validation_ok, validation_errors) = OutputValidator.validate(
                        output_helper, result
                    )

                    if not validation_ok:
                        raise InvalidLLMOutputType(validation_errors)
                break

            except Exception as e:
                traceback_errors = traceback.format_exc()
                self.logger.log(f"Failed with error: {traceback_errors}", logging.ERROR)
                if self.on_failure:
                    self.on_failure(code_to_run, traceback_errors)

                if (
                    not self.context.config.use_error_correction_framework
                    or retry_count >= self.context.config.max_retries
                ):
                    raise e

                retry_count += 1

                self.logger.log(
                    f"Failed to execute code retrying with a correction framework "
                    f"[retry number: {retry_count}]",
                    level=logging.WARNING,
                )

                # TODO - Move this implement to main execute function
                # Temporarily done for test cases this is to be fixed move to the main function
                code_to_run = self._retry_run_code(
                    code_to_run, self.context, self.logger, e
                )

        self.context.add("last_code_executed", code_manager.last_code_executed)

        return LogicUnitOutput(
            result,
            True,
            "Code Executed Successfully",
            {"content_type": "response", "value": ResponseSerializer.serialize(result)},
            final_track_output=True,
        )

    def _retry_run_code(
        self,
        code: str,
        context: PipelineContext,
        logger: Logger,
        e: Exception,
    ) -> str:
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
        if self.on_retry:
            return self.on_retry(code, e)
        else:
            raise e
