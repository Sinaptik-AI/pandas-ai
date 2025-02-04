from typing import Optional

import duckdb
import pandas as pd

from pandasai.dataframe.virtual_dataframe import VirtualDataFrame
from pandasai.query_builders import ViewQueryBuilder

from .. import LOCAL_SOURCE_TYPES
from ..exceptions import MaliciousQueryError
from ..helpers.sql_sanitizer import is_sql_query_safe
from .duck_db_connection_manager import DuckDBConnectionManager
from .loader import DatasetLoader
from .local_loader import LocalDatasetLoader
from .semantic_layer_schema import SemanticLayerSchema, Source
from .sql_loader import SQLDatasetLoader


class ViewDatasetLoader(SQLDatasetLoader):
    """
    Loader for view-based datasets.
    """

    def __init__(self, schema: SemanticLayerSchema, dataset_path: str):
        super().__init__(schema, dataset_path)
        self.dependencies_datasets = self._get_dependencies_datasets()
        self.schema_dependencies_dict: dict[
            str, DatasetLoader
        ] = self._get_dependencies_schemas()
        self.source: Source = list(self.schema_dependencies_dict.values())[
            0
        ].schema.source
        self._query_builder: ViewQueryBuilder = ViewQueryBuilder(
            schema, self.schema_dependencies_dict
        )

    @property
    def query_builder(self) -> ViewQueryBuilder:
        return self._query_builder

    def _get_dependencies_datasets(self) -> set[str]:
        return {
            table.split(".")[0]
            for relation in self.schema.relations
            for table in (relation.from_, relation.to)
        }

    def _get_dependencies_schemas(self) -> dict[str, DatasetLoader]:
        dependency_dict = {
            dep: DatasetLoader.create_loader_from_path(f"{self.org_name}/{dep}")
            for dep in self.dependencies_datasets
        }

        loaders = list(dependency_dict.values())
        base_source = loaders[0].schema.source

        for loader in loaders[1:]:
            if not base_source.is_compatible_source(loader.schema.source):
                raise ValueError(
                    f"Source in loader with schema {loader.schema} is not compatible with the first loader's source."
                )

        return dependency_dict

    def load(self) -> VirtualDataFrame:
        return VirtualDataFrame(
            schema=self.schema,
            data_loader=ViewDatasetLoader(self.schema, self.dataset_path),
            path=self.dataset_path,
        )

    def execute_local_query(self, query) -> pd.DataFrame:
        try:
            db_manager = DuckDBConnectionManager()

            for loader in list(self.schema_dependencies_dict.values()):
                if isinstance(loader, LocalDatasetLoader):
                    loader.register_table()

            return db_manager.sql(query).df()
        except duckdb.Error as e:
            raise RuntimeError(f"SQL execution failed: {e}") from e

    def execute_query(self, query: str, params: Optional[list] = None) -> pd.DataFrame:
        source_type = self.source.type
        connection_info = self.source.connection

        formatted_query = self.query_builder.format_query(query)

        if source_type in LOCAL_SOURCE_TYPES:
            return self.execute_local_query(formatted_query)

        load_function = self._get_loader_function(source_type)

        if not is_sql_query_safe(formatted_query):
            raise MaliciousQueryError(
                "The SQL query is deemed unsafe and will not be executed."
            )
        try:
            dataframe: pd.DataFrame = load_function(
                connection_info, formatted_query, params
            )
            return dataframe

        except ModuleNotFoundError as e:
            raise ImportError(
                f"{source_type.capitalize()} connector not found. Please install the pandasai_sql[{source_type}] library, e.g. `pip install pandasai_sql[{source_type}]`."
            ) from e

        except Exception as e:
            raise RuntimeError(
                f"Failed to execute query for '{source_type}' with: {formatted_query}"
            ) from e
