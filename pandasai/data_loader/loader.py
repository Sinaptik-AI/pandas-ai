import copy
import hashlib
import importlib
import os
from typing import Any, Optional

import pandas as pd
import yaml

from pandasai.dataframe.base import DataFrame
from pandasai.dataframe.virtual_dataframe import VirtualDataFrame
from pandasai.exceptions import InvalidDataSourceType
from pandasai.helpers.path import find_project_root
from pandasai.helpers.sql_sanitizer import sanitize_sql_table_name

from ..constants import (
    LOCAL_SOURCE_TYPES,
    SUPPORTED_SOURCE_CONNECTORS,
)
from .query_builder import QueryBuilder
from .semantic_layer_schema import SemanticLayerSchema
from .transformation_manager import TransformationManager
from .view_query_builder import ViewQueryBuilder


class DatasetLoader:
    def __init__(self):
        self.schema: Optional[SemanticLayerSchema] = None
        self.query_builder: Optional[QueryBuilder] = None
        self.dataset_path: Optional[str] = None

    def load(self, dataset_path: str) -> DataFrame:
        """
        Load data into a DataFrame based on the provided dataset path or schema.

        Args:
            dataset_path (Optional[str]): Path to the dataset file. Provide this or `schema`, not both.
            schema (Optional[SemanticLayerSchema]): Schema object for the dataset. Provide this or `dataset_path`, not both.

        Returns:
            DataFrame: A new DataFrame instance with loaded data.

        Raises:
            ValueError: If both `dataset_path` and `schema` are provided, or neither is provided.
        """
        self.dataset_path = dataset_path
        schema = self._read_local_schema()
        return self._build_dataset(schema, dataset_path)

    def _build_dataset(
        self, schema: SemanticLayerSchema, dataset_path: str
    ) -> DataFrame:
        self.schema = schema
        self.dataset_path = dataset_path
        is_view = schema.view

        self.query_builder = (
            ViewQueryBuilder(schema) if is_view else QueryBuilder(schema)
        )

        source_type = schema.source.type
        if source_type in LOCAL_SOURCE_TYPES:
            df = self._load_from_local_source()
            df = self._filter_columns(df)
            df = self._apply_transformations(df)

            df = pd.DataFrame(df)

            return DataFrame(
                df,
                schema=schema,
                path=dataset_path,
            )
        else:
            data_loader = self.copy()
            return VirtualDataFrame(
                schema=schema,
                data_loader=data_loader,
                path=dataset_path,
            )

    def _get_abs_dataset_path(self):
        return os.path.join(find_project_root(), "datasets", self.dataset_path)

    def _read_local_schema(self) -> SemanticLayerSchema:
        schema_path = os.path.join(str(self._get_abs_dataset_path()), "schema.yaml")
        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"Schema file not found: {schema_path}")

        with open(schema_path, "r") as file:
            raw_schema = yaml.safe_load(file)
            raw_schema["name"] = sanitize_sql_table_name(raw_schema["name"])
            return SemanticLayerSchema(**raw_schema)

    def _get_loader_function(self, source_type: str):
        """
        Get the loader function for a specified data source type.
        """
        try:
            module_name = SUPPORTED_SOURCE_CONNECTORS[source_type]
            module = importlib.import_module(module_name)

            if source_type not in {
                "mysql",
                "postgres",
                "cockroach",
                "sqlite",
                "cockroachdb",
            }:
                raise InvalidDataSourceType(
                    f"Unsupported data source type: {source_type}"
                )

            return getattr(module, f"load_from_{source_type}")

        except KeyError:
            raise InvalidDataSourceType(f"Unsupported data source type: {source_type}")

        except ImportError as e:
            raise ImportError(
                f"{source_type.capitalize()} connector not found. "
                f"Please install the {SUPPORTED_SOURCE_CONNECTORS[source_type]} library."
            ) from e

    def _read_csv_or_parquet(self, file_path: str, _format: str) -> DataFrame:
        if _format == "parquet":
            return DataFrame(
                pd.read_parquet(file_path),
                schema=self.schema,
                path=self.dataset_path,
            )
        elif _format == "csv":
            return DataFrame(
                pd.read_csv(file_path),
                schema=self.schema,
                path=self.dataset_path,
            )
        else:
            raise ValueError(f"Unsupported file format: {_format}")

    def _load_from_local_source(self) -> pd.DataFrame:
        source_type = self.schema.source.type

        if source_type not in LOCAL_SOURCE_TYPES:
            raise InvalidDataSourceType(
                f"Unsupported local source type: {source_type}. Supported types are: {LOCAL_SOURCE_TYPES}."
            )

        filepath = os.path.join(
            str(self._get_abs_dataset_path()),
            self.schema.source.path,
        )

        return self._read_csv_or_parquet(filepath, source_type)

    def load_head(self) -> pd.DataFrame:
        query = self.query_builder.get_head_query()
        return self.execute_query(query)

    def get_row_count(self) -> int:
        query = self.query_builder.get_row_count()
        result = self.execute_query(query)
        return result.iloc[0, 0]

    def execute_query(self, query: str, params: Optional[list] = None) -> pd.DataFrame:
        source = self.schema.source
        source_type = source.type
        connection_info = source.connection

        formatted_query = self.query_builder.format_query(query)

        if not source_type:
            raise ValueError("Source type is missing in the schema.")

        load_function = self._get_loader_function(source_type)

        try:
            return load_function(connection_info, formatted_query, params)
        except Exception as e:
            raise RuntimeError(
                f"Failed to execute query for '{source_type}' with: {formatted_query}"
            ) from e

    def _filter_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter DataFrame columns based on schema columns if specified.

        Args:
            df (pd.DataFrame): Input DataFrame to filter

        Returns:
            pd.DataFrame: DataFrame with only columns specified in schema
        """
        if not self.schema or not self.schema.columns:
            return df

        schema_columns = [col.name for col in self.schema.columns]
        df_columns = df.columns.tolist()
        columns_to_keep = [col for col in df_columns if col in schema_columns]
        return df[columns_to_keep]

    def _apply_transformations(self, df: pd.DataFrame) -> pd.DataFrame:
        if not self.schema.transformations:
            return df

        transformation_manager = TransformationManager(df)
        return transformation_manager.apply_transformations(self.schema.transformations)

    @staticmethod
    def _anonymize(value: Any) -> Any:
        if not isinstance(value, str) or "@" not in value:
            return value
        try:
            local, domain = value.rsplit("@", 1)
            return f"{hashlib.md5(local.encode()).hexdigest()}@{domain}"
        except ValueError:
            return value

    def copy(self) -> "DatasetLoader":
        """
        Create a new independent copy of the current DatasetLoader instance.

        Returns:
            DatasetLoader: A new instance with the same state.
        """
        new_loader = DatasetLoader()
        new_loader.schema = copy.deepcopy(self.schema)
        new_loader.query_builder = copy.deepcopy(self.query_builder)
        new_loader.dataset_path = self.dataset_path
        return new_loader
