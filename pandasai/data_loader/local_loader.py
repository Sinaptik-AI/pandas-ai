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

    def _apply_grouping(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply grouping and aggregation based on schema group_by and column expressions.

        Args:
            df (pd.DataFrame): Input DataFrame to group

        Returns:
            pd.DataFrame: Grouped and aggregated DataFrame
        """
        if not self.schema.group_by:
            return df

        # Map of SQL aggregation names to pandas aggregation functions
        agg_map = {
            "AVG": "mean",
            "MAX": "max",
            "MIN": "min",
            "SUM": "sum",
        }

        # Create aggregation dictionary for columns with expressions
        agg_dict = {}
        for col in self.schema.columns:
            if col.expression:
                # Only process if expression starts with a supported aggregation function
                expr_upper = col.expression.upper()
                if any(expr_upper.startswith(f"{func}(") for func in agg_map):
                    func_name = expr_upper.split("(")[0]
                    agg_dict[col.name] = agg_map[func_name]

        if agg_dict:
            df = df.groupby(self.schema.group_by).agg(agg_dict).reset_index()

        return df

    def _filter_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter DataFrame columns based on schema columns if specified.
        Also handles column aliases if present.

        Args:
            df (pd.DataFrame): Input DataFrame to filter

        Returns:
            pd.DataFrame: DataFrame with filtered columns and applied aliases
        """
        if not self.schema.columns:
            return df

        # First apply any grouping and aggregation
        df = self._apply_grouping(df)

        # Create a list of columns to keep and their aliases
        column_mapping = {}
        for col in self.schema.columns:
            if col.alias:
                column_mapping[col.name] = col.alias
            else:
                column_mapping[col.name] = col.name

        # Filter columns and apply aliases
        df = df[[col.name for col in self.schema.columns]]
        df = df.rename(columns=column_mapping)

        return df

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
