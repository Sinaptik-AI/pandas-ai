import re
from typing import Any, Iterable

import pandasai.pandas as pd


class OutputValidator:
    @staticmethod
    def validate(expected_type, result: dict[str, Any]) -> tuple[bool, Iterable[str]]:
        """
        Validate 'type' and 'value' from the result dict.

        Args:
            result (dict[str, Any]): The result of code execution in
                dict representation. Should have the following schema:
                {
                    "type": <expected_type_name>,
                    "value": <generated_value>
                }

        Returns:
             (tuple(bool, Iterable(str)):
                Boolean value whether the result matches output type
                and collection of logs containing messages about
                'type' or 'value' mismatches.
        """
        validation_logs = []
        result_type, result_value = result.get("type"), result.get("value")

        type_ok = OutputValidator.validate_type(result_type, expected_type)
        if not type_ok:
            validation_logs.append(
                f"The result dict contains inappropriate 'type'. "
                f"Expected '{expected_type}', actual '{result_type}'."
            )
        value_ok = OutputValidator.validate_value(result_value, expected_type)
        if not value_ok:
            validation_logs.append(
                f"result value {repr(result_value)} seems to be inappropriate "
                f"for the type '{expected_type}'."
            )

        return all((type_ok, value_ok)), validation_logs

    def validate_type(self, expected_type: str) -> bool:
        return self == expected_type if expected_type else True

    def validate_value(self, expected_type: str) -> bool:
        if not expected_type:
            return True
        elif expected_type == "number":
            return isinstance(self, (int, float))
        elif expected_type == "string":
            return isinstance(self, str)
        elif expected_type == "dataframe":
            return isinstance(self, (pd.DataFrame, pd.Series))
        elif expected_type == "plot":
            if not isinstance(self, str):
                return False

            path_to_plot_pattern = r"^(\/[\w.-]+)+(/[\w.-]+)*$|^[^\s/]+(/[\w.-]+)*$"
            return bool(re.match(path_to_plot_pattern, self))
