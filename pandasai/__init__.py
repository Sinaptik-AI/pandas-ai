# -*- coding: utf-8 -*-
"""
PandasAI is a wrapper around a LLM to make dataframes conversational
"""

from pandasai.smart_dataframe import SmartDataframe
from pandasai.smart_datalake import SmartDatalake

from .agent import Agent
from .engine import set_pd_engine
from .helpers.cache import Cache
from .skills import skill


def clear_cache(filename: str = None):
    """Clear the cache"""
    cache = Cache(filename) if filename else Cache()

    cache.clear()


__all__ = [
    "Agent",
    "clear_cache",
    "skill",
    "set_pd_engine",
    "pandas",
    "SmartDataframe",
    "SmartDatalake",
]
