from dataclasses import dataclass


@dataclass
class JudgePipelineInput:
    query: str
    code: str

    def __init__(self, query: str, code: str) -> None:
        self.query = query
        self.code = code
