import copy
import hashlib
import importlib
import os
import re
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

    def load(
        self,
        dataset_path: Optional[str] = None,
        schema: Optional[SemanticLayerSchema] = None,
    ) -> DataFrame:
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
        if not dataset_path and not schema:
            raise ValueError("Either 'dataset_path' or 'schema' must be provided.")
        if dataset_path and schema:
            raise ValueError(
                "Provide only one of 'dataset_path' or 'schema', not both."
            )

        if dataset_path:
            self.dataset_path = dataset_path
            self._load_schema()
        elif schema:
            self.schema = schema

        if self.schema.source.view:
            self.query_builder = ViewQueryBuilder(self.schema)
        else:
            self.query_builder = QueryBuilder(self.schema)

        source_type = self.schema.source.type
        if source_type in LOCAL_SOURCE_TYPES:
            # in case of direct schema passed set dataset path to schema.source.path if exists
            if not self.dataset_path and self.schema.source.path:
                self.dataset_path = self.schema.source.path

            df = self._load_from_local_source()
            df = self._filter_columns(df)
            df = self._apply_group_by(df)
            df = self._apply_transformations(df)

            # Convert to pandas DataFrame while preserving internal data
            df = pd.DataFrame(df)

            return DataFrame(
                df,
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
        schema_path = os.path.join(str(self._get_abs_dataset_path()), "schema.yaml")
        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"Schema file not found: {schema_path}")

        with open(schema_path, "r") as file:
            raw_schema = yaml.safe_load(file)
            raw_schema["name"] = sanitize_sql_table_name(raw_schema["name"])
            self.schema = SemanticLayerSchema(**raw_schema)

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

        if source_type == "sqlite":
            query = self.query_builder.build_query()
            return self.execute_query(query)

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

    def _apply_group_by(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply group by operations and aggregations to the DataFrame.

        Args:
            df (pd.DataFrame): Input DataFrame

        Returns:
            pd.DataFrame: DataFrame with group by operations applied
        """
        if not self.schema.group_by or not self.schema.columns:
            return df

        # First handle CASE expressions in group by columns
        group_cols = []
        for col_name in self.schema.group_by:
            col = next((c for c in self.schema.columns if c.name == col_name), None)
            if col and col.expression and "case when" in col.expression.lower():
                # Create the computed column for grouping
                case_expr = col.expression
                df[col.name] = self._evaluate_case_expression(df, case_expr)
            group_cols.append(col_name)

        # Map SQL functions to pandas functions
        sql_to_pandas = {
            "avg": "mean",
            "count": "size",
            "sum": "sum",
            "min": "min",
            "max": "max",
        }

        # Get aggregation expressions for each column
        agg_dict = {}
        for col in self.schema.columns:
            if col.expression:
                if col.expression == "count(*)":
                    # For count(*), we'll use size
                    agg_dict[col.name] = pd.NamedAgg(
                        column=group_cols[0], aggfunc="size"
                    )
                else:
                    match = re.match(r"(\w+)\(([\w\s*]+)\)", col.expression)
                    if match:
                        func, column = match.groups()
                        pandas_func = sql_to_pandas.get(func.lower(), func.lower())
                        agg_dict[col.name] = pd.NamedAgg(
                            column=column.strip(), aggfunc=pandas_func
                        )

        if not agg_dict:
            return df

        # Apply group by and aggregations
        result_df = df.groupby(group_cols, as_index=False, dropna=False).agg(**agg_dict)

        # Sort by group by columns and convert categoricals to string
        result_df = result_df.sort_values(group_cols).reset_index(drop=True)
        for col in group_cols:
            if pd.api.types.is_categorical_dtype(result_df[col]):
                result_df[col] = result_df[col].astype(str)
        return result_df

    def _evaluate_case_expression(self, df: pd.DataFrame, case_expr: str) -> pd.Series:
        """Evaluate a SQL CASE expression on a DataFrame

        Args:
            df (pd.DataFrame): Input DataFrame
            case_expr (str): SQL CASE expression

        Returns:
            pd.Series: Result of the CASE expression
        """
        # Remove 'case' and 'end' keywords and split into when/then pairs
        expr = case_expr.replace("case", "").replace("end", "").strip()
        conditions = []
        values = []
        else_value = None

        # Split into when/then pairs
        parts = expr.split("when")[1:]  # Skip the first empty part

        for part in parts:
            if "then" not in part:
                continue

            condition, value = part.split("then", 1)
            # Handle ELSE clause if present
            if "else" in value:
                value, else_part = value.split("else", 1)
                else_value = else_part.strip().strip("'")

            conditions.append(condition.strip())
            values.append(value.strip().strip("'"))

        # Create the result series with the else value
        result = pd.Series([else_value] * len(df), index=df.index)

        # Apply conditions in reverse order to handle overlapping conditions
        for condition, value in zip(reversed(conditions), reversed(values)):
            mask = df.eval(condition)
            result[mask] = value

        # Create a categorical with the values in the order they appear
        all_values = values + [else_value]
        result = pd.Categorical(result, categories=all_values, ordered=True)

        return result

    def _anonymize(self, value: Any) -> Any:
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
