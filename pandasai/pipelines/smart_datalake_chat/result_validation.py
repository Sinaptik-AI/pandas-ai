import logging
from typing import Any
from pandasai.helpers.logger import Logger
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
        if result is not None:
            if isinstance(result, dict):
                (
                    validation_ok,
                    validation_logs,
                ) = pipeline_context.get_intermediate_value(
                    "output_type_helper"
                ).validate(result)
                if not validation_ok:
                    logger.log("\n".join(validation_logs), level=logging.WARNING)
                    pipeline_context.query_exec_tracker.add_step(
                        {
                            "type": "Validating Output",
                            "success": False,
                            "message": "Output Validation Failed",
                        }
                    )
                else:
                    pipeline_context.query_exec_tracker.add_step(
                        {
                            "type": "Validating Output",
                            "success": True,
                            "message": "Output Validation Successful",
                        }
                    )

            pipeline_context.add_intermediate_value("last_result", result)
            logger.log(f"Answer: {result}")

        logger.log(
            f"Executed in: {pipeline_context.query_exec_tracker.get_execution_time()}s"
        )

        return result
