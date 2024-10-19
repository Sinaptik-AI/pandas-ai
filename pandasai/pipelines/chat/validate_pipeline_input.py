from typing import Any, List

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
        Validates that all connectors are SQL connectors and belong to the same datasource
        when direct_sql is True.
        """

        if not self.context.config.direct_sql:
            return False

        if not all(hasattr(df, "is_sql_connector") for df in dfs):
            raise InvalidConfigError(
                "Direct SQL requires all connectors to be SQLConnectors"
            )

        if len(dfs) > 1:
            first_connector = dfs[0]
            if not all(connector.equals(first_connector) for connector in dfs[1:]):
                raise InvalidConfigError(
                    "Direct SQL requires all connectors to belong to the same datasource "
                    "and have the same credentials"
                )

        return True

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
