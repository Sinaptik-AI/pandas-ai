from dataclasses import dataclass
from typing import Any


@dataclass
class LogicUnitOutput:
    """
    Pipeline step output
    """

    output: Any
    message: str
    success: bool
    metadata: dict

    def __init__(
        self,
        output: Any = None,
        success: bool = False,
        message: str = None,
        metadata: dict = None,
    ):
        self.output = output
        self.message = message
        self.metadata = metadata
        self.success = success
