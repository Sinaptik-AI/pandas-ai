from typing import Any, List

from pandasai.connectors.sql import SQLConnector
from pandasai.exceptions import InvalidConfigError
from pandasai.pipelines.logic_unit_output import LogicUnitOutput

from ...connectors import BaseConnector
from ..base_logic_unit import BaseLogicUnit
from ..pipeline_context import PipelineContext


class ValidatePipelineInput(BaseLogicUnit):
    """
    Validates pipeline input
    """

    pass

    def _validate_direct_sql(self, dfs: List[BaseConnector]) -> bool:
        """
        Raises error if they don't belong sqlconnector or have different credentials
        Args:
            dfs (List[BaseConnector]): list of BaseConnectors

        Raises:
            InvalidConfigError: Raise Error in case of config is set but criteria is not met
        """

        if self.context.config.direct_sql:
            if all((isinstance(df, SQLConnector) and df.equals(dfs[0])) for df in dfs):
                return True
            else:
                raise InvalidConfigError(
                    "Direct requires all SQLConnector and they belong to same datasource "
                    "and have same credentials"
                )
        return False

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
        self._validate_direct_sql(self.context.dfs)
        return LogicUnitOutput(input, True, "Input Validation Successful")
