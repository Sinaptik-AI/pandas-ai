from abc import abstractmethod
from ..exceptions import (
    MethodNotImplementedError,
)


class BaseCallback:
    """Base class to implement new callbacks"""

    @abstractmethod
    def on_code(self, response: str):
        """Run on code response"""
        raise MethodNotImplementedError("Must have implemented this.")


class StdoutCallback(BaseCallback):
    """Callback that prints to std out."""

    def on_code(self, response: str):
        """Write the code response to std out"""
        print(response)
