from abc import ABC, abstractmethod
from typing import Any


class AbstractPipeline(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def run(self, input: Any) -> Any:
        """
        This method will return output according to
        Implementation."""
        raise NotImplementedError("Run method must be implemented")
