import os

import pandas as pd
import yaml

from pandasai.dataframe.base import DataFrame
from pandasai.exceptions import MethodNotImplementedError
from pandasai.helpers.sql_sanitizer import sanitize_sql_table_name

from .. import ConfigManager
from ..constants import (
    LOCAL_SOURCE_TYPES,
)
from .query_builder import QueryBuilder
from .semantic_layer_schema import SemanticLayerSchema
from .transformation_manager import TransformationManager
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
        schema = cls._read_schema_file(dataset_path)
        return DatasetLoader.create_loader_from_schema(schema, dataset_path)

    @staticmethod
    def _read_schema_file(dataset_path: str) -> SemanticLayerSchema:
        schema_path = os.path.join(dataset_path, "schema.yaml")

        file_manager = ConfigManager.get().file_manager

        if not file_manager.exists(schema_path):
            raise FileNotFoundError(f"Schema file not found: {schema_path}")

        schema_file = file_manager.load(schema_path)
        raw_schema = yaml.safe_load(schema_file)
        raw_schema["name"] = sanitize_sql_table_name(raw_schema["name"])
        return SemanticLayerSchema(**raw_schema)

    def load(self) -> DataFrame:
        """
        Load data into a DataFrame based on the provided dataset path or schema.

        Returns:
            DataFrame: A new DataFrame instance with loaded data.

        """
        raise MethodNotImplementedError("Loader not instantiated")

    def _apply_transformations(self, df: pd.DataFrame) -> pd.DataFrame:
        if not self.schema.transformations:
            return df

        transformation_manager = TransformationManager(df)
        return transformation_manager.apply_transformations(self.schema.transformations)
