import copy
import hashlib
import importlib
import os
from datetime import datetime, timedelta
from typing import Any, Optional

import pandas as pd
import yaml

from pandasai.dataframe.base import DataFrame
from pandasai.dataframe.virtual_dataframe import VirtualDataFrame
from pandasai.exceptions import InvalidDataSourceType
from pandasai.helpers.path import find_project_root

from ..constants import (
    LOCAL_SOURCE_TYPES,
    SUPPORTED_SOURCE_CONNECTORS,
)
from .query_builder import QueryBuilder
from .semantic_layer_schema import SemanticLayerSchema


class DatasetLoader:
    def __init__(self):
        self.schema: Optional[SemanticLayerSchema] = None
        self.dataset_path = None

    def load(self, dataset_path: str) -> DataFrame:
        """Load data based on the provided dataset path.

        Args:
            dataset_path (str): Path in the format 'organization/dataset_name'

        Returns:
            DataFrame: A new PandaAI DataFrame instance with loaded data.
        """
        self.dataset_path = dataset_path
        self._load_schema()

        source_type = self.schema.source.type
        if source_type in LOCAL_SOURCE_TYPES:
            cache_file = self._get_cache_file_path()

            if self._is_cache_valid(cache_file):
                cache_format = self.schema.destination.format
                return self._read_csv_or_parquet(cache_file, cache_format)

            df = self._load_from_local_source()
            df = self._apply_transformations(df)

            # Convert to pandas DataFrame while preserving internal data
            df = pd.DataFrame(df._data)
            self._cache_data(df, cache_file)

            return DataFrame(
                df._data,
                schema=self.schema,
                name=self.schema.name,
                description=self.schema.description,
                path=dataset_path,
            )
        else:
            data_loader = self.copy()
            return VirtualDataFrame(
                schema=self.schema,
                data_loader=data_loader,
                path=dataset_path,
            )

    def _get_abs_dataset_path(self):
        return os.path.join(find_project_root(), "datasets", self.dataset_path)

    def _load_schema(self):
        schema_path = os.path.join(self._get_abs_dataset_path(), "schema.yaml")
        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"Schema file not found: {schema_path}")

        with open(schema_path, "r") as file:
            raw_schema = yaml.safe_load(file)
            self.schema = SemanticLayerSchema(**raw_schema)

    def _get_cache_file_path(self) -> str:
        if self.schema.destination.path:
            return os.path.join(
                str(self._get_abs_dataset_path()), self.schema.destination.path
            )

        file_extension = (
            "parquet" if self.schema.destination.format == "parquet" else "csv"
        )
        return os.path.join(str(self._get_abs_dataset_path()), f"data.{file_extension}")

    def _is_cache_valid(self, cache_file: str) -> bool:
        if not os.path.exists(cache_file):
            return False

        file_mtime = datetime.fromtimestamp(os.path.getmtime(cache_file))
        update_frequency = self.schema.update_frequency

        if update_frequency and update_frequency == "weekly":
            return file_mtime > datetime.now() - timedelta(weeks=1)

        return False

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

    def _read_csv_or_parquet(self, file_path: str, format: str) -> DataFrame:
        if format == "parquet":
            return DataFrame(
                pd.read_parquet(file_path),
                schema=self.schema,
                path=self.dataset_path,
                name=self.schema.name,
                description=self.schema.description,
            )
        elif format == "csv":
            return DataFrame(
                pd.read_csv(file_path),
                schema=self.schema,
                path=self.dataset_path,
                name=self.schema.name,
                description=self.schema.description,
            )
        else:
            raise ValueError(f"Unsupported file format: {format}")

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
        query_builder = QueryBuilder(self.schema)
        query = query_builder.get_head_query()
        return self.execute_query(query)

    def get_row_count(self) -> int:
        query_builder = QueryBuilder(self.schema)
        query = query_builder.get_row_count()
        result = self.execute_query(query)
        return result.iloc[0, 0]

    def execute_query(self, query: str) -> pd.DataFrame:
        source = self.schema.get("source", {})
        source_type = source.get("type")
        connection_info = source.get("connection", {})

        if not source_type:
            raise ValueError("Source type is missing in the schema.")

        load_function = self._get_loader_function(source_type)

        try:
            return load_function(connection_info, query)
        except Exception as e:
            raise RuntimeError(
                f"Failed to execute query for source type '{source_type}' with query: {query}"
            ) from e

    def _apply_transformations(self, df: pd.DataFrame) -> pd.DataFrame:
        for transformation in self.schema.transformations or []:
            transformation_type = transformation.type
            transformation_column = transformation.params["column"]
            if transformation_type == "anonymize":
                df[transformation_column] = df[transformation_column].apply(
                    self._anonymize
                )
            elif transformation_type == "convert_timezone":
                df[transformation_column] = pd.to_datetime(
                    df[transformation_column]
                ).dt.tz_convert(transformation.params["to"])
        return df

    @staticmethod
    def _anonymize(value: Any) -> Any:
        if not isinstance(value, str) or "@" not in value:
            return value
        try:
            local, domain = value.rsplit("@", 1)
            return f"{hashlib.md5(local.encode()).hexdigest()}@{domain}"
        except ValueError:
            return value

    def _cache_data(self, df: pd.DataFrame, cache_file: str):
        cache_format = self.schema.destination.format
        if cache_format == "parquet":
            df.to_parquet(cache_file, index=False)
        elif cache_format == "csv":
            df.to_csv(cache_file, index=False)

    def copy(self) -> "DatasetLoader":
        """
        Create a new independent copy of the current DatasetLoader instance.

        Returns:
            DatasetLoader: A new instance with the same state.
        """
        new_loader = DatasetLoader()
        new_loader.schema = copy.deepcopy(self.schema)
        new_loader.dataset_path = self.dataset_path
        return new_loader
