from dataclasses import dataclass
from typing import Any

from pandasai.pipelines.step_output import StepOutput


@dataclass
class StepInput:
    """
    Pipeline step output
    """

    input: Any
    last_step_output: StepOutput

    def __init__(self, input: Any, last_step_output: StepOutput = None):
        self.output = input
        self.last_step_output = last_step_output
