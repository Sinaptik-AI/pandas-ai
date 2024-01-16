from dataclasses import dataclass


@dataclass
class ErrorCorrectionPipelineInput:
    code: str
    exception: Exception

    def __init__(self, code: str, exception: Exception):
        self.code = code
        self.exception = exception
