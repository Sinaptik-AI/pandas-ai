# -*- coding: utf-8 -*-
"""
PandaAI is a wrapper around a LLM to make dataframes conversational
"""

import os
import re
from io import BytesIO
from typing import List
from zipfile import ZipFile

import pandas as pd

from pandasai.config import APIKeyManager, ConfigManager
from pandasai.constants import DEFAULT_API_URL
from pandasai.data_loader.semantic_layer_schema import (
    Column,
    SemanticLayerSchema,
    Source,
)
from pandasai.exceptions import DatasetNotFound, InvalidConfigError, PandaAIApiKeyError
from pandasai.helpers.path import find_project_root
from pandasai.helpers.session import get_pandaai_session

from .agent import Agent
from .constants import SQL_SOURCE_TYPES
from .core.cache import Cache
from .data_loader.loader import DatasetLoader
from .data_loader.semantic_layer_schema import (
    Column,
    SQLConnectionConfig,
    SqliteConnectionConfig,
)
from .dataframe import DataFrame, VirtualDataFrame
from .helpers.sql_sanitizer import sanitize_sql_table_name
from .smart_dataframe import SmartDataframe
from .smart_datalake import SmartDatalake


def create(
    path: str,
    df: DataFrame = None,
    connector: dict = None,
    name: str = None,
    description: str = None,
    columns: List[dict] = None,
):
    """
    Args:
        path (str): Path in the format 'organization/dataset'. This specifies
            the location where the dataset should be created.
        df (DataFrame): The DataFrame containing the data to save.
        name (str, optional): The name of the dataset. Defaults to None.
            If not provided, a name will be automatically generated.
        description (str, optional): A textual description of the dataset.
            Defaults to None.
        columns (List[dict], optional): A list of dictionaries defining the column schema.
            Each dictionary should have keys like 'name', 'type', and optionally
            'description' to describe individual columns. Defaults to None.
    """
    # Validate path format
    path_parts = path.split("/")
    if len(path_parts) != 2:
        raise ValueError("Path must be in format 'organization/dataset'")

    org_name, dataset_name = path_parts
    if not org_name or not dataset_name:
        raise ValueError("Both organization and dataset names are required")

    # Validate organization and dataset name format
    if not bool(re.match(r"^[a-z0-9\-_]+$", org_name)):
        raise ValueError(
            "Organization name must be lowercase and use hyphens instead of spaces (e.g. 'my-org')"
        )

    if not bool(re.match(r"^[a-z0-9\-_]+$", dataset_name)):
        raise ValueError(
            "Dataset name must be lowercase and use hyphens instead of spaces (e.g. 'my-dataset')"
        )

    # Create full path with slugified dataset name
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

    is_valid_sql_config = (
        df is None and connector is not None and connector["type"] in SQL_SOURCE_TYPES
    )

    if df is not None:
        # Save DataFrame to parquet
        df.to_parquet(os.path.join(dataset_directory, "data.parquet"), index=False)
        schema = df.schema

    elif is_valid_sql_config:
        schema = SemanticLayerSchema(name=connector.get("table"), source=connector)
    else:
        raise InvalidConfigError("Unsupported connector type for semantic layer")

    schema.name = name or schema.name
    schema.description = description or schema.description
    if columns:
        schema.columns = list(map(lambda column: Column(**column), columns))

    with open(schema_path, "w") as yml_file:
        yml_file.write(schema.to_yaml())

    print(f"Dataset saved successfully to path: {dataset_directory}")

    return _dataset_loader.load(dataset_directory)


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
    return DataFrame(data._data, name=name)


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
