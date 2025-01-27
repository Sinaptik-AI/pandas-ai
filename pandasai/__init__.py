# -*- coding: utf-8 -*-
"""
PandaAI is a wrapper around a LLM to make dataframes conversational
"""

import os
import re
from io import BytesIO
from typing import List, Optional, Union
from zipfile import ZipFile

import pandas as pd

from pandasai.config import APIKeyManager, ConfigManager
from pandasai.constants import DEFAULT_API_URL
from pandasai.data_loader.semantic_layer_schema import (
    Column,
    Relation,
    SemanticLayerSchema,
    Source,
)
from pandasai.exceptions import DatasetNotFound, InvalidConfigError, PandaAIApiKeyError
from pandasai.helpers.path import find_project_root, get_validated_dataset_path
from pandasai.helpers.session import get_pandaai_session

from .agent import Agent
from .constants import LOCAL_SOURCE_TYPES, SQL_SOURCE_TYPES
from .core.cache import Cache
from .data_loader.loader import DatasetLoader
from .data_loader.semantic_layer_schema import (
    Column,
)
from .dataframe import DataFrame, VirtualDataFrame
from .helpers.sql_sanitizer import sanitize_sql_table_name
from .smart_dataframe import SmartDataframe
from .smart_datalake import SmartDatalake


def create(
    path: str,
    df: Optional[DataFrame] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
    columns: Optional[List[dict]] = None,
    source: Optional[dict] = None,
    relations: Optional[List[dict]] = None,
) -> Union[DataFrame, VirtualDataFrame]:
    """
    Creates a new dataset at the specified path with optional metadata, schema,
    and data source configurations.

    Args:
        path (str): Path in the format 'organization/dataset'. Specifies the location
            where the dataset should be created. The organization and dataset names
            must be lowercase, with hyphens instead of spaces.
        df (DataFrame, optional): The DataFrame containing the data to save. If not
            provided, a connector must be specified to define the dataset source.
        name (str, optional): The name of the dataset. Defaults to None. If not
            provided, a name will be automatically generated or inferred.
        description (str, optional): A textual description of the dataset. Defaults
            to None.
        columns (List[dict], optional): A list of dictionaries defining the column schema.
            Each dictionary should include keys such as 'name', 'type', and optionally
            'description' to describe individual columns. If not provided, the schema
            will be inferred from the DataFrame or connector.
        source (dict, optional): A dictionary specifying the data source configuration.
            Required if `df` is not provided. The connector may include keys like 'type',
            'table', or 'view' to define the data source type and structure.
        relations (dict, optional): A dictionary specifying relationships between tables
            when the dataset is created as a view. Each relationship should be defined
            using keys such as 'type', 'source', and 'target'.

    Returns:
        Union[DataFrame, VirtualDataFrame]: The created dataset object. This may be
        a physical DataFrame if data is saved locally, or a VirtualDataFrame if
        defined using a connector or relations.

    Raises:
        ValueError: If the `path` format is invalid, the organization or dataset
            name contains unsupported characters, or a dataset already exists at
            the specified path.
        InvalidConfigError: If neither `df` nor a valid `source` is provided.

    Example:
        >>> create(
        ...     path="my-org/my-dataset",
        ...     df=my_dataframe,
        ...     name="My Dataset",
        ...     description="This is a sample dataset.",
        ...     columns=[
        ...         {"name": "id", "type": "integer", "description": "Primary key"},
        ...         {"name": "name", "type": "string", "description": "Name of the item"},
        ...     ],
        ... )
        Dataset saved successfully to path: datasets/my-org/my-dataset
    """
    if df is not None and not isinstance(df, DataFrame):
        raise ValueError("df must be a PandaAI DataFrame")

    org_name, dataset_name = get_validated_dataset_path(path)

    dataset_directory = os.path.join(
        find_project_root(), "datasets", org_name, dataset_name
    )

    # Check if dataset already exists
    if os.path.exists(dataset_directory):
        schema_path = os.path.join(dataset_directory, "schema.yaml")
        if os.path.exists(schema_path):
            raise ValueError(f"Dataset already exists at path: {path}")

    os.makedirs(dataset_directory, exist_ok=True)

    # Save schema to yaml
    schema_path = os.path.join(dataset_directory, "schema.yaml")

    if df is None and source is None:
        raise InvalidConfigError("Please provide either a DataFrame or a source")

    if df is not None:
        schema = df.schema
        df.to_parquet(os.path.join(dataset_directory, "data.parquet"), index=False)
    elif source.get("type") == "sqlite" and source.get("table"):
        schema = SemanticLayerSchema(name=source.get("table"), source=Source(**source))
        df = _dataset_loader.load(schema=schema)
        df.to_parquet(os.path.join(dataset_directory, "data.parquet"), index=False)
    elif source.get("table"):
        schema = SemanticLayerSchema(name=source.get("table"), source=Source(**source))
        df = _dataset_loader.load(schema=schema)
    elif source.get("view"):
        name = name or dataset_name
        _relation = [Relation(**relation) for relation in relations or ()]
        schema = SemanticLayerSchema(
            name=name, source=Source(**source), relations=_relation
        )
        df = _dataset_loader.load(schema=schema)

    schema.name = sanitize_sql_table_name(name or schema.name)
    schema.description = description or schema.description
    if columns:
        schema.columns = [Column(**column) for column in columns]
    elif df is not None:
        schema.columns = [
            Column(name=str(name), type=DataFrame.get_column_type(dtype))
            for name, dtype in df.dtypes.items()
        ]

    with open(schema_path, "w") as yml_file:
        yml_file.write(schema.to_yaml())

    print(f"Dataset saved successfully to path: {dataset_directory}")

    return _dataset_loader.load(path)


# Global variable to store the current agent
_current_agent = None

config = ConfigManager()

api_key = APIKeyManager()


def clear_cache(filename: str = None):
    """Clear the cache"""
    cache = Cache(filename) if filename else Cache()
    cache.clear()


def chat(query: str, *dataframes: DataFrame):
    """
    Start a new chat interaction with the assistant on Dataframe(s).

    Args:
        query (str): The query to run against the dataframes.
        *dataframes: Variable number of dataframes to query.

    Returns:
        The result of the query.
    """
    global _current_agent
    if not dataframes:
        raise ValueError("At least one dataframe must be provided.")

    _current_agent = Agent(list(dataframes))
    return _current_agent.chat(query)


def follow_up(query: str):
    """
    Continue the existing chat interaction with the assistant on Dataframe(s).

    Args:
        query (str): The follow-up query to run.

    Returns:
        The result of the query.
    """
    global _current_agent

    if _current_agent is None:
        raise ValueError(
            "No existing conversation. Please use chat() to start a new conversation."
        )

    return _current_agent.follow_up(query)


_dataset_loader = DatasetLoader()


def load(dataset_path: str) -> DataFrame:
    """
    Load data based on the provided dataset path.

    Args:
        dataset_path (str): Path in the format 'organization/dataset_name'.

    Returns:
        DataFrame: A new PandaAI DataFrame instance with loaded data.
    """
    path_parts = dataset_path.split("/")
    if len(path_parts) != 2:
        raise ValueError("The path must be in the format 'organization/dataset'.")

    global _dataset_loader
    dataset_full_path = os.path.join(find_project_root(), "datasets", dataset_path)
    if not os.path.exists(dataset_full_path):
        api_key = os.environ.get("PANDABI_API_KEY", None)
        api_url = os.environ.get("PANDABI_API_URL", DEFAULT_API_URL)
        if not api_url or not api_key:
            raise PandaAIApiKeyError()

        request_session = get_pandaai_session()

        headers = {"accept": "application/json", "x-authorization": f"Bearer {api_key}"}

        file_data = request_session.get(
            "/datasets/pull", headers=headers, params={"path": dataset_path}
        )
        if file_data.status_code != 200:
            raise DatasetNotFound("Dataset not found!")

        with ZipFile(BytesIO(file_data.content)) as zip_file:
            zip_file.extractall(dataset_full_path)

    return _dataset_loader.load(dataset_path)


def read_csv(filepath: str) -> DataFrame:
    data = pd.read_csv(filepath)
    name = f"table_{sanitize_sql_table_name(filepath)}"
    return DataFrame(data, name=name)


__all__ = [
    "Agent",
    "DataFrame",
    "VirtualDataFrame",
    "clear_cache",
    "pandas",
    "chat",
    "follow_up",
    "load",
    # Deprecated
    "SmartDataframe",
    "SmartDatalake",
]
