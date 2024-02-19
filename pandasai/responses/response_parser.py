from abc import ABC, abstractmethod
from typing import Any

from PIL import Image

from pandasai.exceptions import MethodNotImplementedError


class IResponseParser(ABC):
    @abstractmethod
    def parse(self, result: dict) -> Any:
        """
        Parses result from the chat input
        Args:
            result (dict): result contains type and value
        Raises:
            ValueError: if result is not a dictionary with valid key

        Returns:
            Any: Returns depending on the user input
        """
        raise MethodNotImplementedError


class ResponseParser(IResponseParser):
    _context = None

    def __init__(self, context) -> None:
        """
        Initialize the ResponseParser with Context from Agent
        Args:
            context (Context): context contains the config and logger
        """
        self._context = context

    def parse(self, result: dict) -> Any:
        """
        Parses result from the chat input
        Args:
            result (dict): result contains type and value
        Raises:
            ValueError: if result is not a dictionary with valid key

        Returns:
            Any: Returns depending on the user input
        """
        if not isinstance(result, dict) or any(
            key not in result for key in ["type", "value"]
        ):
            raise ValueError("Unsupported result format")

        if result["type"] == "plot":
            return self.format_plot(result)
        else:
            return result["value"]

    def format_plot(self, result: dict) -> Any:
        """
        Display matplotlib plot against a user query.

        If `open_charts` option set to `False`, the chart won't be displayed.

        Args:
            result (dict): result contains type and value
        Returns:
            Any: Returns depending on the user input
        """
        if self._context._config.open_charts:
            with Image.open(result["value"]) as img:
                img.show()

        return result["value"]
