from typing import Any, List, Optional, Union

import pandas as pd

from ..exceptions import UnsupportedTransformation
from .semantic_layer_schema import Transformation


class TransformationManager:
    """Manages data transformations on pandas DataFrames."""

    def __init__(self, df: pd.DataFrame):
        """Initialize the TransformationManager with a DataFrame.

        Args:
            df (pd.DataFrame): The DataFrame to transform
        """
        self.df = df.copy()
        self.transformation_handlers = {
            "anonymize": lambda p: self.anonymize(p.column),
            "convert_timezone": lambda p: self.convert_timezone(p.column, p.to),
            "to_lowercase": lambda p: self.to_lowercase(p.column),
            "to_uppercase": lambda p: self.to_uppercase(p.column),
            "strip": lambda p: self.strip(p.column),
            "round_numbers": lambda p: self.round_numbers(p.column, p.decimals),
            "scale": lambda p: self.scale(p.column, p.factor),
            "format_date": lambda p: self.format_date(p.column, p.format),
            "to_numeric": lambda p: self.to_numeric(
                p.column, getattr(p, "errors", "coerce")
            ),
            "to_datetime": lambda p: self.to_datetime(
                p.column, getattr(p, "format", None), getattr(p, "errors", "coerce")
            ),
            "fill_na": lambda p: self.fill_na(p.column, p.value),
            "replace": lambda p: self.replace(
                p.column, getattr(p, "old_value", None), getattr(p, "new_value", None)
            ),
            "extract": lambda p: self.extract(p.column, getattr(p, "pattern", None)),
            "truncate": lambda p: self.truncate(
                p.column, getattr(p, "length", None), getattr(p, "add_ellipsis", True)
            ),
            "pad": lambda p: self.pad(
                p.column,
                getattr(p, "width", None),
                getattr(p, "side", "left"),
                getattr(p, "pad_char", " "),
            ),
            "clip": lambda p: self.clip(
                p.column, getattr(p, "lower", None), getattr(p, "upper", None)
            ),
            "bin": lambda p: self.bin(
                p.column, getattr(p, "bins", None), getattr(p, "labels", None)
            ),
            "normalize": lambda p: self.normalize(p.column),
            "standardize": lambda p: self.standardize(p.column),
            "map_values": lambda p: self.map_values(p.column, p.mapping),
            "rename": lambda p: self.rename(p.column, p.new_name),
            "encode_categorical": lambda p: self.encode_categorical(
                p.column, getattr(p, "drop_first", True)
            ),
            "validate_email": lambda p: self.validate_email(
                p.column, getattr(p, "drop_invalid", False)
            ),
            "validate_date_range": lambda p: self.validate_date_range(
                p.column,
                getattr(p, "start_date", None),
                getattr(p, "end_date", None),
                getattr(p, "drop_invalid", False),
            ),
            "normalize_phone": lambda p: self.normalize_phone(
                p.column, getattr(p, "country_code", "+1")
            ),
            "remove_duplicates": lambda p: self.remove_duplicates(
                getattr(p, "columns", None), getattr(p, "keep", "first")
            ),
            "validate_foreign_key": lambda p: self.validate_foreign_key(
                p.column,
                getattr(p, "ref_df", None),
                getattr(p, "ref_column", None),
                getattr(p, "drop_invalid", False),
            ),
            "ensure_positive": lambda p: self.ensure_positive(
                p.column, getattr(p, "drop_negative", False)
            ),
            "standardize_categories": lambda p: self.standardize_categories(
                p.column, getattr(p, "mapping", None)
            ),
        }

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

        Example:
            >>> df = pd.DataFrame({"email": ["user@example.com", "another@domain.com"]})
            >>> manager = TransformationManager(df)
            >>> result = manager.anonymize("email").df
            >>> print(result)
                           email
            0  ****@example.com
            1  *******@domain.com
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

        Example:
            >>> df = pd.DataFrame({"timestamp": ["2024-01-01 12:00:00+00:00"]})
            >>> manager = TransformationManager(df)
            >>> result = manager.convert_timezone("timestamp", "US/Pacific").df
            >>> print(result)
                               timestamp
            0 2024-01-01 04:00:00-08:00
        """
        self.df[column] = pd.to_datetime(self.df[column]).dt.tz_convert(to_timezone)
        return self

    def to_lowercase(self, column: str) -> "TransformationManager":
        """Convert all values in a column to lowercase.

        Args:
            column (str): The column to transform

        Returns:
            TransformationManager: Self for method chaining

        Example:
            >>> df = pd.DataFrame({"text": ["Hello", "WORLD"]})
            >>> manager = TransformationManager(df)
            >>> result = manager.to_lowercase("text").df
            >>> print(result)
                  text
            0  hello
            1  world
        """
        self.df[column] = self.df[column].str.lower()
        return self

    def to_uppercase(self, column: str) -> "TransformationManager":
        """Convert all values in a column to uppercase.

        Args:
            column (str): The column to transform

        Returns:
            TransformationManager: Self for method chaining

        Example:
            >>> df = pd.DataFrame({"text": ["Hello", "world"]})
            >>> manager = TransformationManager(df)
            >>> result = manager.to_uppercase("text").df
            >>> print(result)
                  text
            0  HELLO
            1  WORLD
        """
        self.df[column] = self.df[column].str.upper()
        return self

    def strip(self, column: str) -> "TransformationManager":
        """Remove leading and trailing whitespace from values in a column.

        Args:
            column (str): The column to transform

        Returns:
            TransformationManager: Self for method chaining

        Example:
            >>> df = pd.DataFrame({"text": [" Hello ", "  World  "]})
            >>> manager = TransformationManager(df)
            >>> result = manager.strip("text").df
            >>> print(result)
                  text
            0  Hello
            1  World
        """
        self.df[column] = self.df[column].str.strip()
        return self

    def round_numbers(self, column: str, decimals: int) -> "TransformationManager":
        """Round numeric values in a column to specified decimal places.

        Args:
            column (str): The column to transform
            decimals (int): Number of decimal places to round to

        Returns:
            TransformationManager: Self for method chaining

        Example:
            >>> df = pd.DataFrame({"price": [10.126, 20.983]})
            >>> manager = TransformationManager(df)
            >>> result = manager.round_numbers("price", 2).df
            >>> print(result)
                price
            0  10.13
            1  20.98
        """
        self.df[column] = self.df[column].round(decimals)
        return self

    def scale(self, column: str, factor: float) -> "TransformationManager":
        """Multiply values in a column by a scaling factor.

        Args:
            column (str): The column to transform
            factor (float): The scaling factor to multiply by

        Returns:
            TransformationManager: Self for method chaining

        Example:
            >>> df = pd.DataFrame({"price": [10, 20]})
            >>> manager = TransformationManager(df)
            >>> result = manager.scale("price", 1.1).df  # 10% increase
            >>> print(result)
                price
            0  11.0
            1  22.0
        """
        self.df[column] = self.df[column] * factor
        return self

    def format_date(self, column: str, date_format: str) -> "TransformationManager":
        """Format datetime values in a column according to the specified format.

        Args:
            column (str): The column to transform
            date_format (str): The desired date format (e.g., "%Y-%m-%d")

        Returns:
            TransformationManager: Self for method chaining

        Example:
            >>> df = pd.DataFrame({"date": ["2025-01-01 12:30:45"]})
            >>> manager = TransformationManager(df)
            >>> result = manager.format_date("date", "%Y-%m-%d").df
            >>> print(result)
                     date
            0  2025-01-01
        """
        self.df[column] = self.df[column].dt.strftime(date_format)
        return self

    def to_numeric(
        self, column: str, errors: str = "coerce"
    ) -> "TransformationManager":
        """Convert values in a column to numeric type.

        Args:
            column (str): The column to transform
            errors (str): How to handle parsing errors:
                         'raise': raise an exception
                         'coerce': set errors to NaN
                         'ignore': return the input

        Returns:
            TransformationManager: Self for method chaining

        Example:
            >>> df = pd.DataFrame({"value": ["1.23", "4.56", "invalid"]})
            >>> manager = TransformationManager(df)
            >>> result = manager.to_numeric("value", errors="coerce").df
            >>> print(result)
                value
            0   1.23
            1   4.56
            2    NaN
        """
        self.df[column] = pd.to_numeric(self.df[column], errors=errors)
        return self

    def to_datetime(
        self, column: str, _format: Optional[str] = None, errors: str = "coerce"
    ) -> "TransformationManager":
        """Convert values in a column to datetime type.

        Args:
            column (str): The column to transform
            _format (Optional[str]): Expected date format of the input
            errors (str): How to handle parsing errors

        Returns:
            TransformationManager: Self for method chaining

        Example:
            >>> df = pd.DataFrame({"date": ["2025-01-01", "invalid"]})
            >>> manager = TransformationManager(df)
            >>> result = manager.to_datetime("date", errors="coerce").df
            >>> print(result)
                        date
            0  2025-01-01
            1         NaT
        """
        self.df[column] = pd.to_datetime(self.df[column], format=_format, errors=errors)
        return self

    def fill_na(self, column: str, value: Any) -> "TransformationManager":
        """Fill NA/NaN values in a column with the specified value.

        Args:
            column (str): The column to transform
            value (Any): Value to use to fill NA/NaN

        Returns:
            TransformationManager: Self for method chaining

        Example:
            >>> df = pd.DataFrame({"value": [1, None, 3]})
            >>> manager = TransformationManager(df)
            >>> result = manager.fill_na("value", 0).df
            >>> print(result)
                value
            0      1
            1      0
            2      3
        """
        self.df[column] = self.df[column].fillna(value)
        return self

    def replace(
        self, column: str, old_value: str, new_value: str
    ) -> "TransformationManager":
        """Replace occurrences of old_value with new_value in the column.

        Args:
            column (str): The column to transform
            old_value (str): Value to replace
            new_value (str): Replacement value

        Returns:
            TransformationManager: Self for method chaining

        Example:
            >>> df = pd.DataFrame({"status": ["active", "inactive", "active"]})
            >>> manager = TransformationManager(df)
            >>> result = manager.replace("status", "inactive", "disabled").df
            >>> print(result)
                  status
            0    active
            1  disabled
            2    active
        """
        self.df[column] = self.df[column].str.replace(old_value, new_value)
        return self

    def extract(self, column: str, pattern: str) -> "TransformationManager":
        """Extract text matching the regex pattern.

        Args:
            column (str): The column to transform
            pattern (str): Regular expression pattern to extract

        Returns:
            TransformationManager: Self for method chaining

        Example:
            >>> df = pd.DataFrame({"text": ["ID: 123", "ID: 456"]})
            >>> manager = TransformationManager(df)
            >>> result = manager.extract("text", r"ID: (\d+)").df
            >>> print(result)
                text
            0   123
            1   456
        """
        self.df[column] = self.df[column].str.extract(pattern, expand=False)
        return self

    def truncate(
        self, column: str, length: int, add_ellipsis: bool = True
    ) -> "TransformationManager":
        """Truncate strings to specified length.

        Args:
            column (str): The column to transform
            length (int): Maximum length of string
            add_ellipsis (bool): Whether to add "..." to truncated strings

        Returns:
            TransformationManager: Self for method chaining

        Example:
            >>> df = pd.DataFrame({"text": ["very long text", "short"]})
            >>> manager = TransformationManager(df)
            >>> result = manager.truncate("text", 8, add_ellipsis=True).df
            >>> print(result)
                     text
            0  very...
            1    short
        """

        def _truncate(x):
            if pd.isna(x):
                return x
            s = str(x)
            if len(s) <= length:
                return s
            if add_ellipsis:
                # Reserve 3 characters for ellipsis
                return s[: length - 3].rstrip() + "..."
            return s[:length]

        self.df[column] = self.df[column].apply(_truncate)
        return self

    def pad(
        self, column: str, width: int, side: str = "left", pad_char: str = " "
    ) -> "TransformationManager":
        """Pad strings to a specified width.

        Args:
            column (str): The column to transform
            width (int): Desired string width
            side (str): Side to pad ('left' or 'right')
            pad_char (str): Character to use for padding

        Returns:
            TransformationManager: Self for method chaining

        Example:
            >>> df = pd.DataFrame({"id": ["1", "23"]})
            >>> manager = TransformationManager(df)
            >>> result = manager.pad("id", width=3, side="left", pad_char="0").df
            >>> print(result)
                id
            0  001
            1  023
        """
        if side == "left":
            self.df[column] = self.df[column].str.rjust(width, pad_char)
        else:
            self.df[column] = self.df[column].str.ljust(width, pad_char)
        return self

    def clip(
        self, column: str, lower: Optional[float] = None, upper: Optional[float] = None
    ) -> "TransformationManager":
        """Clip values to be between lower and upper bounds.

        Args:
            column (str): The column to transform
            lower (Optional[float]): Lower bound
            upper (Optional[float]): Upper bound

        Returns:
            TransformationManager: Self for method chaining

        Example:
            >>> df = pd.DataFrame({"score": [0, 50, 100, 150]})
            >>> manager = TransformationManager(df)
            >>> result = manager.clip("score", lower=0, upper=100).df
            >>> print(result)
                score
            0      0
            1     50
            2    100
            3    100
        """
        self.df[column] = self.df[column].clip(lower=lower, upper=upper)
        return self

    def bin(
        self,
        column: str,
        bins: Union[int, List[float]],
        labels: Optional[List[str]] = None,
    ) -> "TransformationManager":
        """Bin continuous data into discrete intervals.

        Args:
            column (str): The column to transform
            bins (Union[int, List[float]]): Number of bins or bin edges
            labels (Optional[List[str]]): Labels for the bins

        Returns:
            TransformationManager: Self for method chaining

        Example:
            >>> df = pd.DataFrame({"age": [25, 35, 45, 55]})
            >>> manager = TransformationManager(df)
            >>> result = manager.bin("age", bins=[0, 30, 50, 100],
            ...                     labels=["Young", "Middle", "Senior"]).df
            >>> print(result)
                   age
            0   Young
            1  Middle
            2  Middle
            3  Senior
        """
        self.df[column] = pd.cut(self.df[column], bins=bins, labels=labels)
        return self

    def normalize(self, column: str) -> "TransformationManager":
        """Normalize values to 0-1 range using min-max scaling.

        Args:
            column (str): The column to transform

        Returns:
            TransformationManager: Self for method chaining

        Example:
            >>> df = pd.DataFrame({"score": [0, 50, 100]})
            >>> manager = TransformationManager(df)
            >>> result = manager.normalize("score").df
            >>> print(result)
                score
            0    0.0
            1    0.5
            2    1.0
        """
        min_val = self.df[column].min()
        max_val = self.df[column].max()
        self.df[column] = (self.df[column] - min_val) / (max_val - min_val)
        return self

    def standardize(self, column: str) -> "TransformationManager":
        """Standardize values using z-score normalization.

        Args:
            column (str): The column to transform

        Returns:
            TransformationManager: Self for method chaining

        Example:
            >>> df = pd.DataFrame({"score": [1, 2, 3]})
            >>> manager = TransformationManager(df)
            >>> result = manager.standardize("score").df
            >>> print(result)
                     score
            0   -1.224745
            1    0.000000
            2    1.224745
        """
        mean = self.df[column].mean()
        std = self.df[column].std()
        self.df[column] = (self.df[column] - mean) / std
        return self

    def map_values(self, column: str, mapping: dict) -> "TransformationManager":
        """Map values to new values using a dictionary.

        Args:
            column (str): The column to transform
            mapping (dict): Dictionary mapping old values to new values
                          e.g., {"Apple Inc.": "Apple", "Apple Computer": "Apple"}

        Returns:
            TransformationManager: Self for method chaining

        Example:
            >>> df = pd.DataFrame({"grade": ["A", "B", "C"]})
            >>> mapping = {"A": 4.0, "B": 3.0, "C": 2.0}
            >>> manager = TransformationManager(df)
            >>> result = manager.map_values("grade", mapping).df
            >>> print(result)
                grade
            0    4.0
            1    3.0
            2    2.0
        """
        self.df[column] = self.df[column].map(mapping)
        return self

    def encode_categorical(
        self, column: str, drop_first: bool = True
    ) -> "TransformationManager":
        """One-hot encode categorical variables.

        Args:
            column (str): The column to transform
            drop_first (bool): Whether to drop the first category

        Returns:
            TransformationManager: Self for method chaining

        Example:
            >>> df = pd.DataFrame({"color": ["red", "blue", "red"]})
            >>> manager = TransformationManager(df)
            >>> result = manager.encode_categorical("color").df
            >>> print(result)
                   color_red
            0           1
            1           0
            2           1
        """
        encoded = pd.get_dummies(self.df[column], prefix=column, drop_first=drop_first)
        self.df = pd.concat([self.df.drop(columns=[column]), encoded], axis=1)
        return self

    def validate_email(
        self, column: str, drop_invalid: bool = False
    ) -> "TransformationManager":
        """Validate email format in a column.

        Args:
            column (str): The column to validate
            drop_invalid (bool): If True, drop rows with invalid emails

        Returns:
            TransformationManager: Self for method chaining

        Example:
            >>> df = pd.DataFrame({"email": ["user@example.com", "invalid.email"]})
            >>> manager = TransformationManager(df)
            >>> result = manager.validate_email("email", drop_invalid=True).df
            >>> print(result)
                           email
            0  user@example.com
        """
        import re

        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

        def is_valid_email(x):
            if pd.isna(x):
                return False
            return bool(re.match(email_pattern, str(x)))

        if drop_invalid:
            self.df = self.df[self.df[column].apply(is_valid_email)]
        else:
            self.df[f"{column}_valid"] = self.df[column].apply(is_valid_email)
        return self

    def validate_date_range(
        self, column: str, start_date: str, end_date: str, drop_invalid: bool = False
    ) -> "TransformationManager":
        """Validate dates are within a specified range.

        Args:
            column (str): The column to validate
            start_date (str): Minimum valid date (YYYY-MM-DD)
            end_date (str): Maximum valid date (YYYY-MM-DD)
            drop_invalid (bool): If True, drop rows with invalid dates

        Returns:
            TransformationManager: Self for method chaining

        Example:
            >>> df = pd.DataFrame({"date": ["2024-01-01", "2025-12-31"]})
            >>> manager = TransformationManager(df)
            >>> result = manager.validate_date_range(
            ...     "date", "2024-01-01", "2024-12-31", drop_invalid=True).df
            >>> print(result)
                        date
            0  2024-01-01
        """
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)

        def is_valid_date(x):
            if pd.isna(x):
                return False
            date = pd.to_datetime(x, errors="coerce")
            if pd.isna(date):
                return False
            return start <= date <= end

        if drop_invalid:
            self.df = self.df[self.df[column].apply(is_valid_date)]
        else:
            self.df[f"{column}_valid"] = self.df[column].apply(is_valid_date)
        return self

    def normalize_phone(
        self, column: str, country_code: str = "+1"
    ) -> "TransformationManager":
        """Normalize phone numbers to a standard format.

        Args:
            column (str): The column to transform
            country_code (str): Default country code to prepend

        Returns:
            TransformationManager: Self for method chaining

        Example:
            >>> df = pd.DataFrame({"phone": ["123-456-7890", "(123) 456-7890"]})
            >>> manager = TransformationManager(df)
            >>> result = manager.normalize_phone("phone", country_code="+1").df
            >>> print(result)
                         phone
            0  +1-123-456-7890
            1  +1-123-456-7890
        """

        def clean_phone(x):
            if pd.isna(x):
                return x
            # Remove all non-digit characters
            phone = "".join(filter(str.isdigit, str(x)))

            # Handle different cases
            if len(phone) == 10:  # Standard US number
                return f"{country_code}-{phone[:3]}-{phone[3:6]}-{phone[6:]}"
            elif len(phone) > 10:  # International number
                return f"+{phone[:-10]}-{phone[-10:-7]}-{phone[-7:-4]}-{phone[-4:]}"
            return x  # Return original if format unknown

        self.df[column] = self.df[column].apply(clean_phone)
        return self

    def remove_duplicates(
        self, columns: Union[str, List[str]], keep: str = "first"
    ) -> "TransformationManager":
        """Remove duplicate rows based on specified columns.

        Args:
            columns (Union[str, List[str]]): Column(s) to identify duplicates
            keep (str): Which duplicate to keep ('first', 'last', or False)

        Returns:
            TransformationManager: Self for method chaining

        Example:
            >>> df = pd.DataFrame({
            ...     "id": [1, 2, 1],
            ...     "name": ["John", "Jane", "John"]
            ... })
            >>> manager = TransformationManager(df)
            >>> result = manager.remove_duplicates(["name"]).df
            >>> print(result)
                id  name
            0   1  John
            1   2  Jane
        """
        self.df = self.df.drop_duplicates(subset=columns, keep=keep)
        return self

    def validate_foreign_key(
        self,
        column: str,
        ref_df: pd.DataFrame,
        ref_column: str,
        drop_invalid: bool = False,
    ) -> "TransformationManager":
        """Validate foreign key references against another DataFrame.

        Args:
            column (str): The column containing foreign keys
            ref_df (pd.DataFrame): Reference DataFrame
            ref_column (str): Column in reference DataFrame to check against
            drop_invalid (bool): If True, drop rows with invalid references

        Returns:
            TransformationManager: Self for method chaining

        Example:
            >>> orders = pd.DataFrame({"user_id": [1, 2, 3]})
            >>> users = pd.DataFrame({"id": [1, 2]})
            >>> manager = TransformationManager(orders)
            >>> result = manager.validate_foreign_key(
            ...     "user_id", users, "id", drop_invalid=True).df
            >>> print(result)
                user_id
            0        1
            1        2
        """
        valid_values = set(ref_df[ref_column].unique())

        def is_valid_reference(x):
            if pd.isna(x):
                return False
            return x in valid_values

        if drop_invalid:
            self.df = self.df[self.df[column].apply(is_valid_reference)]
        else:
            self.df[f"{column}_valid"] = self.df[column].apply(is_valid_reference)
        return self

    def ensure_positive(
        self, column: str, drop_negative: bool = False
    ) -> "TransformationManager":
        """Ensure numeric values are positive.

        Args:
            column (str): The column to validate
            drop_negative (bool): If True, drop rows with negative values

        Returns:
            TransformationManager: Self for method chaining

        Example:
            >>> df = pd.DataFrame({"score": [-1, 0, 1]})
            >>> manager = TransformationManager(df)
            >>> result = manager.ensure_positive("score", drop_negative=True).df
            >>> print(result)
                score
            1      0
            2      1
        """
        if drop_negative:
            self.df = self.df[self.df[column] >= 0].copy()
        else:
            self.df[column] = self.df[column].clip(lower=0)
        return self

    def standardize_categories(
        self, column: str, mapping: dict
    ) -> "TransformationManager":
        """Standardize categorical values using a mapping dictionary.

        Args:
            column (str): The column to transform
            mapping (dict): Dictionary mapping variations to standard forms
                          e.g., {"Apple Inc.": "Apple", "Apple Computer": "Apple"}

        Returns:
            TransformationManager: Self for method chaining

        Example:
            >>> df = pd.DataFrame({"company": ["Apple Inc.", "Apple Computer"]})
            >>> mapping = {"Apple Inc.": "Apple", "Apple Computer": "Apple"}
            >>> manager = TransformationManager(df)
            >>> result = manager.standardize_categories("company", mapping).df
            >>> print(result)
                company
            0      Apple
            1      Apple
        """
        self.df[column] = self.df[column].replace(mapping)
        return self

    def rename(self, column: str, new_name: str) -> "TransformationManager":
        """Rename a column.

        Args:
            column (str): The current column name
            new_name (str): The new name for the column

        Returns:
            TransformationManager: Self for method chaining

        Example:
            >>> df = pd.DataFrame({"old_name": [1, 2, 3]})
            >>> manager = TransformationManager(df)
            >>> result = manager.rename("old_name", "new_name").df
            >>> print(result)
               new_name
            0         1
            1         2
            2         3
        """
        self.df = self.df.rename(columns={column: new_name})
        return self

    def apply_transformations(
        self, transformations: List[Transformation]
    ) -> pd.DataFrame:
        """Apply a list of transformations to the DataFrame.

        Args:
            transformations List[Transformation]: List of transformation configurations

        Returns:
            pd.DataFrame: The transformed DataFrame
        """

        for transformation in transformations:
            transformation_type = transformation.type
            params = transformation.params

            handler = self.transformation_handlers.get(transformation_type)
            if not handler:
                raise UnsupportedTransformation(
                    f"Transformation type '{transformation_type}' is not supported"
                )
            handler(params)

        return self.df
