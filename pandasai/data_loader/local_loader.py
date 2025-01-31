import os

import pandas as pd

from pandasai.dataframe.base import DataFrame
from pandasai.exceptions import InvalidDataSourceType

from ..constants import (
    LOCAL_SOURCE_TYPES,
)
from .loader import DatasetLoader
from .transformation_manager import TransformationManager


class LocalDatasetLoader(DatasetLoader):
    """
    Loader for local datasets (CSV, Parquet).
    """

    def load(self) -> DataFrame:
        df: pd.DataFrame = self._load_from_local_source()
        df = self._filter_columns(df)
        df = self._apply_transformations(df)

        return DataFrame(
            df,
            schema=self.schema,
            path=self.dataset_path,
        )

    def _load_from_local_source(self) -> pd.DataFrame:
        source_type = self.schema.source.type

        if source_type not in LOCAL_SOURCE_TYPES:
            raise InvalidDataSourceType(
                f"Unsupported local source type: {source_type}. Supported types are: {LOCAL_SOURCE_TYPES}."
            )

        filepath = os.path.join(
            self.dataset_path,
            self.schema.source.path,
        )

        return self._read_csv_or_parquet(filepath, source_type)

    def _read_csv_or_parquet(self, file_path: str, file_format: str) -> pd.DataFrame:
        if file_format == "parquet":
            df = pd.read_parquet(file_path)
        elif file_format == "csv":
            df = pd.read_csv(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_format}")

        return df

    def _filter_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter DataFrame columns based on schema columns if specified.

        Args:
            df (pd.DataFrame): Input DataFrame to filter

        Returns:
            pd.DataFrame: DataFrame with only columns specified in schema
        """
        if not self.schema.columns:
            return df

        schema_columns = [col.name for col in self.schema.columns]
        df_columns = df.columns.tolist()
        columns_to_keep = [col for col in df_columns if col in schema_columns]
        return df[columns_to_keep]
