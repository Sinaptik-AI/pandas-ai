from typing import List, Dict
import numpy as np
from pydantic import ValidationError
from pydantic import BaseModel
import concurrent.futures
from pandasai.helpers.df_info import DataFrameType, df_type


class DFValidationResult:
    def __init__(self, passed=True, errors: List[Dict] = []):
        self._passed = passed
        self._errors = errors

    @property
    def passed(self):
        return self._passed

    def errors(self):
        return self._errors

    def add_error(self, error_message: str):
        """
        Add an error message to the validation results.
        """
        self.passed = False
        self._errors.append(error_message)

    def __bool__(self):
        """
        Define the truthiness of ValidationResults.
        """
        return self.passed


class BaseDFValidator:
    def __init__(self, df, n_jobs=1, verbose=False):
        self._df = df
        self._n_jobs = n_jobs
        self._verbose = verbose

    def _validate_batch(self, schema, df_json: List[Dict]):
        """
        Args:
            schema: Pydantic schema
            batch_df: dataframe batch
        """
        try:
            # Create a Pydantic Validator to validate rows of dataframe
            class PdVal(BaseModel):
                df: List[schema]

            PdVal(df=df_json)
            return []

        except ValidationError as e:
            if self._verbose:
                print(e)
            return e.errors()

    def _df_to_list_of_dict(self, df: DataFrameType, dataframe_type: str) -> List[Dict]:
        """
        Create list of dict of dataframe rows on basis of dataframe type
        Supports only polars and pandas dataframe
        """
        if dataframe_type == "pandas":
            return df.to_dict(orient="records")
        elif dataframe_type == "polars":
            return df.to_dicts()
        else:
            []

    def validate(self, schema) -> DFValidationResult:
        """
        Args:
                schema: Pydantic schema to be validated for the dataframe row
        """
        dataframe_type = df_type(self._df)
        if dataframe_type is None:
            raise ValueError("UnSupported DataFrame")

        df_json: List[Dict] = self._df_to_list_of_dict(self._df, dataframe_type)

        errors = self._validate_batch(schema, df_json)

        if len(errors) > 0:
            return DFValidationResult(False, errors)
        else:
            return DFValidationResult(True)


class DFValidator(BaseDFValidator):
    """
    Class to manage Dataframe validation
    """

    def __init__(self, df, n_jobs=1, verbose=False):
        """
        Args:
                        df (Dataframe): DataFrame object
                        n_jobs (int): int
            verbose (bool): bool
        """
        super().__init__(df, n_jobs, verbose)

    def validate(self, schema) -> DFValidationResult:
        """
        Args:
                schema: Pydantic schema to be validated for the dataframe row
        """
        if self._n_jobs > 1:
            # Split data into batches based on num of jobs
            batched_data = np.array_split(self._df, self._n_jobs)
            errors = []

            dataframe_type = df_type(self._df)
            if dataframe_type is None:
                raise ValueError("UnSupported DataFrame")

            # Create Process for parallelism based on number of jobs
            with concurrent.futures.ProcessPoolExecutor(
                max_workers=self._n_jobs
            ) as executor:
                futures = [
                    executor.submit(
                        self._validate_batch,
                        schema,
                        self._df_to_list_of_dict(data, dataframe_type),
                    )
                    for data in batched_data
                ]
                for future in concurrent.futures.as_completed(futures):
                    result = future.result()
                    errors.extend(result)

            if len(errors) > 0:
                return DFValidationResult(False, errors)
            else:
                return DFValidationResult(True)
        else:
            return super().validate(schema)
