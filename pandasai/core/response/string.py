from typing import Any

from .base import BaseResponse


class StringResponse(BaseResponse):
    """
    Class for handling string responses.
    """

    def __init__(self, result: Any = None, last_code_executed: str = None):
        super().__init__(result, "string", last_code_executed)
