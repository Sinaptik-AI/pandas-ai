import base64
import json
from typing import Any

from pandasai.responses.response_parser import IResponseParser


class JsonResponseParser(IResponseParser):
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
        elif result["type"] == "dataframe":
            json_data = json.loads(
                result["value"].to_json(
                    orient="split",
                    date_format="iso",
                    default_handler=str,
                    force_ascii=False,
                )
            )
            return {
                "type": "dataframe",
                "message": "Dataframe created: <dataframe>",
                "value": {
                    "headers": json_data["columns"],
                    "rows": json_data["data"],
                },
            }

        result["message"] = result["value"]

        return result

    def format_plot(self, result: dict) -> Any:
        """
        Display matplotlib plot against a user query.

        If `open_charts` option set to `False`, the chart won't be displayed.

        Args:
            result (dict): result contains type and value
        Returns:
            Any: Returns depending on the user input
        """
        if "data:image/png;base64" not in result["value"]:
            with open(result["value"], "rb") as image_file:
                image_data = image_file.read()
            # Encode the image data to Base64
            base64_image = (
                f"data:image/png;base64,{base64.b64encode(image_data).decode()}"
            )
            result = {
                "type": result["type"],
                "value": base64_image,
            }

        result["message"] = "Plot generated: <plot>"

        return result
