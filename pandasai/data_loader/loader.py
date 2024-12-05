import copy
import os
import yaml
import pandas as pd
from datetime import datetime, timedelta
import hashlib

from pandasai.dataframe.base import DataFrame
from pandasai.dataframe.virtual_dataframe import VirtualDataFrame
from pandasai.exceptions import InvalidDataSourceType
from pandasai.helpers.path import find_project_root
import importlib
from typing import Any
from .query_builder import QueryBuilder
from ..constants import SUPPORTED_SOURCES


class DatasetLoader:
    def __init__(self):
        self.schema = None
        self.dataset_path = None

    def load(self, dataset_path: str, virtualized=False) -> DataFrame:
        self.dataset_path = dataset_path
        self._load_schema()
        self._validate_source_type()
        if not virtualized:
            cache_file = self._get_cache_file_path()

            if self._is_cache_valid(cache_file):
                return self._read_cache(cache_file)

            df = self._load_from_source()
            df = self._apply_transformations(df)
            self._cache_data(df, cache_file)

            table_name = self.schema["source"]["table"]
            table_description = self.schema.get("description", None)

            return DataFrame(
                df,
                schema=self.schema,
                name=table_name,
                description=table_description,
                path=dataset_path,
            )
        else:
            # Initialize new dataset loader for virtualization
            data_loader = self.copy()
            table_name = self.schema["source"]["table"]
            table_description = self.schema.get("description", None)
            return VirtualDataFrame(
                schema=self.schema,
                data_loader=data_loader,
                name=table_name,
                description=table_description,
                path=dataset_path,
            )

    def _load_schema(self):
        schema_path = os.path.join(
            find_project_root(), "datasets", self.dataset_path, "schema.yaml"
        )
        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"Schema file not found: {schema_path}")

        with open(schema_path, "r") as file:
            self.schema = yaml.safe_load(file)

    def _validate_source_type(self):
        source_type = self.schema["source"]["type"]
        if source_type not in SUPPORTED_SOURCES:
            raise ValueError(f"Unsupported database type: {source_type}")

    def _get_cache_file_path(self) -> str:
        if "path" in self.schema["destination"]:
            return os.path.join(
                "datasets", self.dataset_path, self.schema["destination"]["path"]
            )

        file_extension = (
            "parquet" if self.schema["destination"]["format"] == "parquet" else "csv"
        )
        return os.path.join("datasets", self.dataset_path, f"data.{file_extension}")

    def _is_cache_valid(self, cache_file: str) -> bool:
        if not os.path.exists(cache_file):
            return False

        file_mtime = datetime.fromtimestamp(os.path.getmtime(cache_file))
        update_frequency = self.schema["update_frequency"]

        if update_frequency == "weekly":
            return file_mtime > datetime.now() - timedelta(weeks=1)

        return False

    def _read_cache(self, cache_file: str) -> DataFrame:
        cache_format = self.schema["destination"]["format"]
        table_name = self.schema["source"]["table"]
        table_description = self.schema.get("description", None)
        if cache_format == "parquet":
            return DataFrame(
                pd.read_parquet(cache_file),
                schema=self.schema,
                path=self.dataset_path,
                name=table_name,
                description=table_description,
            )
        elif cache_format == "csv":
            return DataFrame(
                pd.read_csv(cache_file),
                schema=self.schema,
                path=self.dataset_path,
                name=table_name,
                description=table_description,
            )
        else:
            raise ValueError(f"Unsupported cache format: {cache_format}")

    def _get_loader_function(self, source_type: str):
        """
        Get the loader function for a specified data source type.
        """
        try:
            module_name = SUPPORTED_SOURCES[source_type]
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
                f"Please install the {SUPPORTED_SOURCES[source_type]} library."
            ) from e

    def _load_from_source(self) -> pd.DataFrame:
        query_builder = QueryBuilder(self.schema)
        query = query_builder.build_query()
        return self.execute_query(query)

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
        for transform in self.schema.get("transformations", []):
            if transform["type"] == "anonymize":
                df[transform["params"]["column"]] = df[
                    transform["params"]["column"]
                ].apply(self._anonymize)
            elif transform["type"] == "convert_timezone":
                df[transform["params"]["column"]] = pd.to_datetime(
                    df[transform["params"]["column"]]
                ).dt.tz_convert(transform["params"]["to"])
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
        cache_format = self.schema["destination"]["format"]
        if cache_format == "parquet":
            df.to_parquet(cache_file, index=False)
        elif cache_format == "csv":
            df.to_csv(cache_file, index=False)
        else:
            raise ValueError(f"Unsupported cache format: {cache_format}")

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
