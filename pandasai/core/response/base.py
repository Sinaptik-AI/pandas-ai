import re

import numpy as np
import pandas as pd

from pandasai.exceptions import InvalidOutputValueMismatch

from .response_types import Chart, DataFrame, Number, String


class ResponseParser:
    def parse(self, result: dict):
        self._validate_response(result)
        return self._generate_response(result)

    def _generate_response(self, result: dict):
        if result["type"] == "number":
            return Number(result)
        elif result["type"] == "string":
            return String(result)
        elif result["type"] == "dataframe":
            return DataFrame(result)
        elif result["type"] == "plot":
            return Chart(result)
        else:
            raise InvalidOutputValueMismatch(f"Invalid output type: {result['type']}")

    def _validate_response(self, result: dict):
        if (
            not isinstance(result, dict)
            or "type" not in result
            or "value" not in result
        ):
            raise InvalidOutputValueMismatch(
                'Result must be in the format of dictionary of type and value like `result = {"type": ..., "value": ... }`'
            )
        elif result["type"] == "number":
            if not isinstance(result["value"], (int, float, np.int64)):
                raise InvalidOutputValueMismatch(
                    "Invalid output: Expected a numeric value for result type 'number', but received a non-numeric value."
                )
        elif result["type"] == "string":
            if not isinstance(result["value"], str):
                raise InvalidOutputValueMismatch(
                    "Invalid output: Expected a string value for result type 'string', but received a non-string value."
                )
        elif result["type"] == "dataframe":
            if not isinstance(result["value"], (pd.DataFrame, pd.Series, dict)):
                raise InvalidOutputValueMismatch(
                    "Invalid output: Expected a Pandas DataFrame or Series, but received an incompatible type."
                )

        elif result["type"] == "plot":
            if not isinstance(result["value"], (str, dict)):
                raise InvalidOutputValueMismatch(
                    "Invalid output: Expected a plot save path str but received an incompatible type."
                )

            if isinstance(result["value"], dict) or (
                isinstance(result["value"], str)
                and "data:image/png;base64" in result["value"]
            ):
                return True

            path_to_plot_pattern = r"^(\/[\w.-]+)+(/[\w.-]+)*$|^[^\s/]+(/[\w.-]+)*$"
            if not bool(re.match(path_to_plot_pattern, result["value"])):
                raise InvalidOutputValueMismatch(
                    "Invalid output: Expected a plot save path str but received an incompatible type."
                )

        return True
