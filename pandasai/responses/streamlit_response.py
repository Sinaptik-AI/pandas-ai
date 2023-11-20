from typing import Any
from pandasai.responses.response_parser import ResponseParser
import pandas as pd


class StreamlitResponse(ResponseParser):
    def __init__(self, context):
        super().__init__(context)

    def format_plot(self, result) -> None:
        """
        Display plot against a user query in Streamlit
        Args:
            result (dict): result contains type and value
        """
        return result["value"]

    def format_dataframe(self, result: dict) -> pd.DataFrame:
        """
        Format dataframe generate against a user query
        Args:
            result (dict): result contains type and value
        Returns:
            Any: Returns depending on the user input
        """
        return result["value"]

    def format_other(self, result) -> Any:
        """
        Format other results
        Args:
            result (dict): result contains type and value
        Returns:
            Any: Returns depending on the user input
        """
        return result["value"]
