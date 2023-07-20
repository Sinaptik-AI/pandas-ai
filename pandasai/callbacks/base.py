from abc import abstractmethod
from ..exceptions import (
    MethodNotImplementedError,
)


class BaseCallback:
    """Base class to implement new callbacks"""

    @abstractmethod
    def on_code(self, response: str):
        raise MethodNotImplementedError("Call method has not been implemented")


class StdoutCallBack(BaseCallback):
    def on_code(self, response: str):
        print(response)


class DefaultCallback(BaseCallback):
    def on_code(self, response: str = None):
        """Do nothing"""
        pass
