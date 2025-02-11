import os

import duckdb
import pandas as pd

from pandasai.dataframe.base import DataFrame
from pandasai.exceptions import InvalidDataSourceType, MaliciousQueryError
from pandasai.query_builders import LocalQueryBuilder

from ..config import ConfigManager
from ..constants import (
    LOCAL_SOURCE_TYPES,
)
from ..helpers.sql_sanitizer import is_sql_query_safe
from .duck_db_connection_manager import DuckDBConnectionManager
from .loader import DatasetLoader
from .semantic_layer_schema import SemanticLayerSchema


class LocalDatasetLoader(DatasetLoader):
    """
    Loader for local datasets (CSV, Parquet).
    """

    def __init__(self, schema: SemanticLayerSchema, dataset_path: str):
        super().__init__(schema, dataset_path)
        self._query_builder: LocalQueryBuilder = LocalQueryBuilder(schema)

    @property
    def query_builder(self) -> LocalQueryBuilder:
        return self._query_builder

    def register_table(self):
        df = self.load()
        db_manager = DuckDBConnectionManager()
        db_manager.register(self.schema.name, df)

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
        file_manager = ConfigManager.get().file_manager
        if file_format == "parquet":
            df = pd.read_parquet(file_manager.abs_path(file_path))
        elif file_format == "csv":
            df = pd.read_csv(file_manager.abs_path(file_path))
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

    def execute_query(self, query: str) -> pd.DataFrame:
        try:
            db_manager = DuckDBConnectionManager()

            if not is_sql_query_safe(query, dialect="duckdb"):
                raise MaliciousQueryError(
                    "The SQL query is deemed unsafe and will not be executed."
                )

            return db_manager.sql(query).df()
        except duckdb.Error as e:
            raise RuntimeError(f"SQL execution failed: {e}") from e
