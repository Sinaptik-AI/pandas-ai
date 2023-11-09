import logging
from typing import Any
from pandasai.helpers.logger import Logger
from pandasai.pipelines.base_logic_unit import BaseLogicUnit
from pandasai.pipelines.pipeline_context import PipelineContext


class ResultValidation(BaseLogicUnit):

    """
    Result Validation Stage
    """

    pass

    def execute(self, input: Any, **kwargs) -> Any:
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
