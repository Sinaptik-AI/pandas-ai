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

# Global variable to store the current agent
_current_agent = None


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

    # debug the current agent
    print("Current agent:", _current_agent)

    if _current_agent is None:
        raise ValueError(
            "No existing conversation. Please use chat() to start a new conversation."
        )

    return _current_agent.follow_up(query)


__all__ = [
    "Agent",
    "clear_cache",
    "skill",
    "set_pd_engine",
    "pandas",
    "SmartDataframe",
    "SmartDatalake",
    "DataFrame",
    "chat",
    "follow_up",
]
