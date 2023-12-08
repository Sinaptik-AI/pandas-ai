from typing import List, Dict
from pydantic import ValidationError
from pydantic import BaseModel
import pandas as pd


class DfValidationResult:
    """
    Validation results for a dataframe.

    Attributes:
        passed: Whether the validation passed or not.
        errors: List of errors if the validation failed.
    """

    _passed: bool
    _errors: List[Dict]

    def __init__(self, passed: bool = True, errors: List[Dict] = None):
        """
        Args:
            passed: Whether the validation passed or not.
            errors: List of errors if the validation failed.
        """
        if errors is None:
            errors = []
        self._passed = passed
        self._errors = errors

    @property
    def passed(self):
        return self._passed

    def errors(self) -> List[Dict]:
        return self._errors

    def add_error(self, error_message: str):
        """
        Add an error message to the validation results.

        Args:
            error_message: Error message to add.
        """
        self._passed = False
        self._errors.append(error_message)

    def __bool__(self) -> bool:
        """
        Define the truthiness of ValidationResults.
        """
        return self.passed


class DfValidator:
    """
    Validate a dataframe using a Pydantic schema.

    Attributes:
        df: dataframe to be validated
    """

    _df: pd.DataFrame

    def __init__(self, df: pd.DataFrame):
        """
        Args:
            df: dataframe to be validated
        """
        self._df = df

    def _validate_batch(self, schema, df_json: List[Dict]):
        """
        Args:
            schema: Pydantic schema
            batch_df: dataframe batch

        Returns:
            list of errors
        """
        try:
            # Create a Pydantic Validator to validate rows of dataframe
            class PdVal(BaseModel):
                df: List[schema]

            PdVal(df=df_json)
            return []

        except ValidationError as e:
            return e.errors()

    def validate(self, schema: BaseModel) -> DfValidationResult:
        """
        Args:
            schema: Pydantic schema to be validated for the dataframe row

        Returns:
            Validation results
        """
        df_json: List[Dict] = self._df.to_dict(orient="records")

        errors = self._validate_batch(schema, df_json)

        return DfValidationResult(len(errors) == 0, errors)
