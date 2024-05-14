from typing import Any

from pandasai.constants import PANDASBI_SETUP_MESSAGE
from pandasai.exceptions import InvalidConfigError
from pandasai.llm.bamboo_llm import BambooLLM
from pandasai.pipelines.logic_unit_output import LogicUnitOutput
from pandasai.pipelines.base_logic_unit import BaseLogicUnit
from pandasai.pipelines.pipeline_context import PipelineContext


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
        if not isinstance(self.context.config.llm, BambooLLM):
            raise InvalidConfigError(
                f"""Visualization Agent works only with BambooLLM follow instructions for setup:\n {PANDASBI_SETUP_MESSAGE}"""
            )

        return LogicUnitOutput(input, True, "Input Validation Successful")
