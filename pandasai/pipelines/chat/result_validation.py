import logging
from typing import Any

from pandasai.helpers.logger import Logger
from pandasai.pipelines.logic_unit_output import LogicUnitOutput

from ...helpers.output_validator import OutputValidator
from ..base_logic_unit import BaseLogicUnit
from ..pipeline_context import PipelineContext


class ResultValidation(BaseLogicUnit):
    """
    Result Validation Stage
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

        result = input
        success = False
        message = None
        if result is not None:
            if isinstance(result, dict):
                (
                    validation_ok,
                    validation_logs,
                ) = OutputValidator.validate(
                    pipeline_context.get("output_type"), result
                )
                if not validation_ok:
                    logger.log("\n".join(validation_logs), level=logging.WARNING)
                    success = False
                    message = "Output Validation Failed"

                else:
                    success = True
                    message = "Output Validation Successful"

            pipeline_context.add("last_result", result)
            logger.log(f"Answer: {result}")

        return LogicUnitOutput(result, success, message)
