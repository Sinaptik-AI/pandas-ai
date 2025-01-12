# -*- coding: utf-8 -*-
"""
PandaAI is a wrapper around a LLM to make dataframes conversational
"""

import os
from io import BytesIO
from typing import List
from zipfile import ZipFile

import pandas as pd

from pandasai.config import APIKeyManager, ConfigManager
from pandasai.exceptions import DatasetNotFound, PandaAIApiKeyError
from pandasai.helpers.path import find_project_root
from pandasai.helpers.request import get_pandaai_session

from .agent import Agent
from .core.cache import Cache
from .data_loader.loader import DatasetLoader
from .dataframe import DataFrame, VirtualDataFrame
from .smart_dataframe import SmartDataframe
from .smart_datalake import SmartDatalake

# Global variable to store the current agent
_current_agent = None

config = ConfigManager()

api_key = APIKeyManager()


def clear_cache(filename: str = None):
    """Clear the cache"""
    cache = Cache(filename) if filename else Cache()
    cache.clear()


def chat(query: str, *dataframes: List[DataFrame]):
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


def load(dataset_path: str, virtualized=False) -> DataFrame:
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
        api_key = os.environ.get("PANDASAI_API_KEY", None)
        api_url = os.environ.get("PANDASAI_API_URL", None)
        if not api_url or not api_key:
            raise PandaAIApiKeyError(
                "Please set the PANDASAI_API_URL and PANDASAI_API_KEY environment variables to pull the dataset from the remote server."
            )

        request_session = get_pandaai_session()

        headers = {"accept": "application/json", "x-authorization": f"Bearer {api_key}"}

        file_data = request_session.get(
            "/datasets/pull", headers=headers, params={"path": dataset_path}
        )
        if file_data.status_code != 200:
            raise DatasetNotFound("Dataset not found!")

        with ZipFile(BytesIO(file_data.content)) as zip_file:
            zip_file.extractall(dataset_full_path)

    return _dataset_loader.load(dataset_path, virtualized)


def read_csv(filepath: str) -> DataFrame:
    data = pd.read_csv(filepath)
    return DataFrame(data._data)


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
