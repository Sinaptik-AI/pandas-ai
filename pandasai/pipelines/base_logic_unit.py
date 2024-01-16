from abc import ABC, abstractmethod
from typing import Any

from pandasai.pipelines.logic_unit_output import LogicUnitOutput


class BaseLogicUnit(ABC):
    """
    Logic units for pipeline each logic unit should be inherited from this Logic unit
    """

    def __init__(self, skip_if=None, on_execution=None, before_execution=None):
        super().__init__()
        self.skip_if = skip_if
        self.on_execution = on_execution
        self.before_execution = before_execution

    @abstractmethod
    def execute(self, input: Any, **kwargs) -> LogicUnitOutput:
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
        raise NotImplementedError("execute method is not implemented.")
