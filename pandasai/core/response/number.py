from typing import Any

from .base import BaseResponse


class NumberResponse(BaseResponse):
    """
    Class for handling numerical responses.
    """

    def __init__(self, value: Any = None, last_code_executed: str = None):
        super().__init__(value, "number", last_code_executed)
