import os
from abc import ABC, abstractmethod

import pandas as pd
import yaml

from pandasai.dataframe.base import DataFrame
from pandasai.exceptions import MethodNotImplementedError
from pandasai.helpers.path import (
    get_validated_dataset_path,
    transform_underscore_to_dash,
)
from pandasai.helpers.sql_sanitizer import sanitize_sql_table_name

from .. import ConfigManager
from ..constants import (
    LOCAL_SOURCE_TYPES,
)
from ..query_builders.base_query_builder import BaseQueryBuilder
from .semantic_layer_schema import SemanticLayerSchema
from .transformation_manager import TransformationManager


class DatasetLoader(ABC):
    def __init__(self, schema: SemanticLayerSchema, dataset_path: str):
        self.schema = schema
        self.org_name, self.dataset_name = get_validated_dataset_path(dataset_path)
        self.dataset_path = f"{self.org_name}/{self.dataset_name}"

    @property
    @abstractmethod
    def query_builder(self) -> BaseQueryBuilder:
        """Abstract property that must be implemented by subclasses."""
        pass

    @abstractmethod
    def execute_query(self, query: str):
        pass

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
        dataset_path = transform_underscore_to_dash(dataset_path)
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
