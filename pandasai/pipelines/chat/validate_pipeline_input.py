from __future__ import annotations
from typing import Any
from pandasai.pipelines.logic_unit_output import LogicUnitOutput

from ..base_logic_unit import BaseLogicUnit
from ..pipeline_context import PipelineContext


class ValidatePipelineInput(BaseLogicUnit):
    """
    Validates pipeline input
    """

    pass

    def execute(self, input: Any, **kwargs) -> Any:
        """
        This method validates pipeline context and configs

        :param input: Your input data.
        :param kwargs: A dictionary of keyword arguments.
            - 'logger' (any): The logger for logging.
            - 'config' (Config): Global configurations for the test
            - 'context' (any): The execution context.

        :return: The result of the execution.
        """
        self.context: PipelineContext = kwargs.get("context")
        return LogicUnitOutput(input, True, "Input Validation Successful")
