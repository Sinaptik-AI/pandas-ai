# -*- coding: utf-8 -*-
"""
PandasAI is a wrapper around a LLM to make dataframes conversational
"""

from typing import List
from pandasai.smart_dataframe import SmartDataframe
from pandasai.smart_datalake import SmartDatalake

from .agent import Agent
from .engine import set_pd_engine
from .helpers.cache import Cache
from .skills import skill
from .dataframe.base import DataFrame


def clear_cache(filename: str = None):
    """Clear the cache"""
    cache = Cache(filename) if filename else Cache()

    cache.clear()


def chat(query: str, *dataframes: List[DataFrame]):
    """
    Run a query against multiple dataframes.

    Args:
        query (str): The query to run against the dataframes.
        *dataframes: Variable number of dataframes to query.

    Returns:
        The result of the query.
    """
    if not dataframes:
        raise ValueError("At least one dataframe must be provided.")

    agent = Agent(list(dataframes))
    return agent.chat(query)


__all__ = [
    "Agent",
    "clear_cache",
    "skill",
    "set_pd_engine",
    "pandas",
    "SmartDataframe",
    "SmartDatalake",
    "DataFrame",
]
