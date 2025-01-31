import os

import yaml

from pandasai.dataframe.base import DataFrame
from pandasai.exceptions import MethodNotImplementedError
from pandasai.helpers.path import find_project_root
from pandasai.helpers.sql_sanitizer import sanitize_sql_table_name

from ..constants import (
    LOCAL_SOURCE_TYPES,
)
from .query_builder import QueryBuilder
from .semantic_layer_schema import SemanticLayerSchema
from .view_query_builder import ViewQueryBuilder


class DatasetLoader:
    def __init__(self, schema: SemanticLayerSchema, dataset_path: str):
        self.schema = schema
        self.dataset_path = dataset_path

    @classmethod
    def create_loader_from_schema(
        cls, schema: SemanticLayerSchema, dataset_path: str
    ) -> "DatasetLoader":
        """
        Factory method to create the appropriate loader based on the dataset type.
        """

        if schema.source and schema.source.type in LOCAL_SOURCE_TYPES:
            from pandasai.data_loader.local_loader import LocalDatasetLoader

            return LocalDatasetLoader(schema, dataset_path)
        elif schema.view:
            from pandasai.data_loader.view_loader import ViewDatasetLoader

            return ViewDatasetLoader(schema, dataset_path)
        else:
            from pandasai.data_loader.sql_loader import SQLDatasetLoader

            return SQLDatasetLoader(schema, dataset_path)

    @classmethod
    def create_loader_from_path(cls, dataset_path: str) -> "DatasetLoader":
        """
        Factory method to create the appropriate loader based on the dataset type.
        """
        schema = cls._read_local_schema(dataset_path)
        return DatasetLoader.create_loader_from_schema(schema, dataset_path)

    @staticmethod
    def _read_local_schema(dataset_path: str) -> SemanticLayerSchema:
        schema_path = os.path.join(
            find_project_root(), "datasets", dataset_path, "schema.yaml"
        )
        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"Schema file not found: {schema_path}")

        with open(schema_path, "r") as file:
            raw_schema = yaml.safe_load(file)
            raw_schema["name"] = sanitize_sql_table_name(raw_schema["name"])
            return SemanticLayerSchema(**raw_schema)

    def load(self) -> DataFrame:
        """
        Load data into a DataFrame based on the provided dataset path or schema.

        Returns:
            DataFrame: A new DataFrame instance with loaded data.

        """
        raise MethodNotImplementedError("Loader not instantiated")

    def _build_dataset(
        self, schema: SemanticLayerSchema, dataset_path: str
    ) -> DataFrame:
        self.schema = schema
        self.dataset_path = dataset_path
        is_view = schema.view

        self.query_builder = (
            ViewQueryBuilder(schema) if is_view else QueryBuilder(schema)
        )

    def _get_abs_dataset_path(self):
        return os.path.join(find_project_root(), "datasets", self.dataset_path)
