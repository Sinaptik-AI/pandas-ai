from typing import List, Optional

import pandas as pd

from ..exceptions import UnsupportedTransformation


class TransformationManager:
    """Manages data transformations on pandas DataFrames."""

    def __init__(self, df: pd.DataFrame):
        """Initialize the TransformationManager with a DataFrame.

        Args:
            df (pd.DataFrame): The DataFrame to transform
        """
        self.df = df.copy()

    def _anonymize(self, value: str) -> str:
        """Anonymize a value by replacing the local part of email with asterisks.
        For non-email values, replace the entire value with asterisks.

        Args:
            value (str): The value to anonymize

        Returns:
            str: The anonymized value
        """
        if pd.isna(value):
            return value

        value_str = str(value)
        if "@" in value_str:
            username, domain = value_str.split("@", 1)
            return "*" * len(username) + "@" + domain
        return "*" * len(value_str)

    def anonymize(self, column: str) -> "TransformationManager":
        """Anonymize values in a specific column.

        Args:
            column (str): The column to anonymize

        Returns:
            TransformationManager: Self for method chaining
        """
        self.df[column] = self.df[column].apply(self._anonymize)
        return self

    def convert_timezone(
        self, column: str, to_timezone: str
    ) -> "TransformationManager":
        """Convert timezone for datetime column.

        Args:
            column (str): The column to convert
            to_timezone (str): Target timezone

        Returns:
            TransformationManager: Self for method chaining
        """
        self.df[column] = pd.to_datetime(self.df[column]).dt.tz_convert(to_timezone)
        return self

    def apply_transformations(
        self, transformations: Optional[List[dict]] = None
    ) -> pd.DataFrame:
        """Apply a list of transformations to the DataFrame.

        Args:
            transformations (Optional[List[dict]]): List of transformation configurations

        Returns:
            pd.DataFrame: The transformed DataFrame
        """
        if not transformations:
            return self.df

        for transformation in transformations:
            transformation_type = transformation.type
            params = transformation.params

            if transformation_type == "anonymize":
                self.anonymize(params["column"])
            elif transformation_type == "convert_timezone":
                self.convert_timezone(params["column"], params["to"])
            else:
                raise UnsupportedTransformation(
                    f"Transformation type '{transformation_type}' is not supported"
                )

        return self.df
