from abc import ABC, abstractmethod
from typing import Any


class BaseLogicUnit(ABC):
    """
    Logic units for pipeline.
    """

    def __init__(self):
        pass

    @abstractmethod
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
        raise NotImplementedError("execute method is not implemented.")
