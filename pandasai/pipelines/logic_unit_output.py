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
    final_track_output: bool

    def __init__(
        self,
        output: Any = None,
        success: bool = False,
        message: str = None,
        metadata: dict = None,
        final_track_output: bool = False,
    ):
        self.output = output
        self.message = message
        self.metadata = metadata
        self.success = success
        self.final_track_output = final_track_output
