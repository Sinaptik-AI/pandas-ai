from typing import Any

from ...pipelines.logic_unit_output import LogicUnitOutput
from ..base_logic_unit import BaseLogicUnit


class CodeCleaning(BaseLogicUnit):
    """
    Code Cleaning Stage
    """

    def execute(self, input: Any, **kwargs) -> LogicUnitOutput:
        # TODO: Take over code cleaning from CodeExecution

        return LogicUnitOutput(
            input,
            True,
            "Code Cleaned Successfully",
        )
