import importlib
from typing import Optional

import pandas as pd

from pandasai.dataframe.virtual_dataframe import VirtualDataFrame
from pandasai.exceptions import InvalidDataSourceType, MaliciousQueryError
from pandasai.helpers.sql_sanitizer import is_sql_query_safe

from ..constants import (
    SUPPORTED_SOURCE_CONNECTORS,
)
from .loader import DatasetLoader
from .query_builder import QueryBuilder
from .semantic_layer_schema import SemanticLayerSchema


class SQLDatasetLoader(DatasetLoader):
    """
    Loader for SQL-based datasets.
    """

    def __init__(self, schema: SemanticLayerSchema, dataset_path: str):
        super().__init__(schema, dataset_path)
        self.query_builder: QueryBuilder = QueryBuilder(schema)

    def load(self) -> VirtualDataFrame:
        return VirtualDataFrame(
            schema=self.schema,
            data_loader=SQLDatasetLoader(self.schema, self.dataset_path),
            path=self.dataset_path,
        )

    def execute_query(self, query: str, params: Optional[list] = None) -> pd.DataFrame:
        source_type = self.schema.source.type
        connection_info = self.schema.source.connection

        formatted_query = self.query_builder.format_query(query)
        load_function = self._get_loader_function(source_type)

        if not is_sql_query_safe(formatted_query):
            raise MaliciousQueryError(
                "The SQL query is deemed unsafe and will not be executed."
            )
        try:
            dataframe: pd.DataFrame = load_function(
                connection_info, formatted_query, params
            )
            return self._apply_transformations(dataframe)

        except ModuleNotFoundError as e:
            raise ImportError(
                f"{source_type.capitalize()} connector not found. Please install the pandasai_sql[{source_type}] library, e.g. `pip install pandasai_sql[{source_type}]`."
            ) from e

        except Exception as e:
            raise RuntimeError(
                f"Failed to execute query for '{source_type}' with: {formatted_query}"
            ) from e

    @staticmethod
    def _get_loader_function(source_type: str):
        try:
            module_name = SUPPORTED_SOURCE_CONNECTORS[source_type]
            module = importlib.import_module(module_name)
            return getattr(module, f"load_from_{source_type}")
        except KeyError:
            raise InvalidDataSourceType(f"Unsupported data source type: {source_type}")
        except ImportError as e:
            raise ImportError(
                f"{source_type.capitalize()} connector not found. Please install the correct library."
            ) from e

    def load_head(self) -> pd.DataFrame:
        query = self.query_builder.get_head_query()
        return self.execute_query(query)

    def get_row_count(self) -> int:
        query = self.query_builder.get_row_count()
        result = self.execute_query(query)
        return result.iloc[0, 0]
