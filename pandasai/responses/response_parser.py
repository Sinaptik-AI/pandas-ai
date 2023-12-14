from abc import ABC, abstractmethod
from typing import Any
from ..helpers.df_info import polars_imported
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
        Initialize the ResponseParser with Context from SmartDataLake
        Args:
            context (Context): context contains the config, logger and engine
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

        if result["type"] == "dataframe":
            return self.format_dataframe(result)
        elif result["type"] == "plot":
            return self.format_plot(result)
        else:
            return self.format_other(result)

    def format_dataframe(self, result: dict) -> Any:
        """
        Format dataframe generate against a user query
        Args:
            result (dict): result contains type and value
        Returns:
            Any: Returns depending on the user input
        """
        from ..smart_dataframe import SmartDataframe

        df = result["value"]
        if self._context.engine == "polars" and polars_imported:
            import polars as pl

            df = pl.from_pandas(df)

        return SmartDataframe(
            df,
            config=self._context._config.__dict__,
            logger=self._context.logger,
        )

    def format_plot(self, result: dict) -> Any:
        """
        Display matplotlib plot against a user query.

        If `open_charts` option set to `False`, the chart won't be displayed.

        Args:
            result (dict): result contains type and value
        Returns:
            Any: Returns depending on the user input
        """
        if not self._context._config.open_charts:
            return

        with Image.open(result["value"]) as img:
            img.show()

        return result["value"]

    def format_other(self, result) -> Any:
        """
        Returns the result generated against a user query other than dataframes
        and plots
        Args:
            result (dict): result contains type and value
        Returns:
            Any: Returns depending on the user input
        """
        return result["value"]
