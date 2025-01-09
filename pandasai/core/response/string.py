from typing import Any

from .base import BaseResponse


class StringResponse(BaseResponse):
    """
    Class for handling string responses.
    """

    def __init__(self, value: Any = None, last_code_executed: str = None):
        super().__init__(value, "string", last_code_executed)
