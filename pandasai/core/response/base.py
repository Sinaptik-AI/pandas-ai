from typing import Any
import json


class BaseResponse:
    """
    Base class for different types of response values.
    """

    def __init__(
        self, result: Any = None, type: str = None, last_code_executed: str = None
    ):
        """
        Initialize the BaseResponse object

        :param result: The result of the response
        :param last_code_executed: The last code executed to generate the result
        :raise ValueError: If result or last_code_executed is None
        """
        if result is None:
            raise ValueError("Result should not be None")
        if type is None:
            raise ValueError("Type should not be None")

        self.value = result
        self.type = type
        self.last_code_executed = last_code_executed

    def __str__(self) -> str:
        """Return the string representation of the response."""
        return str(self.value)

    def __repr__(self) -> str:
        """Return a detailed string representation for debugging."""
        return f"{self.__class__.__name__}(type={self.type!r}, value={self.value!r})"

    def to_dict(self) -> dict:
        """Return a dictionary representation."""
        return self.__dict__

    def to_json(self) -> str:
        """Return a JSON representation."""
        return json.dumps(self.to_dict())
