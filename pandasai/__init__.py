# -*- coding: utf-8 -*-
"""
PandasAI is a wrapper around a LLM to make dataframes conversational
"""
import importlib.metadata

from pandasai.smart_dataframe import SmartDataframe
from pandasai.smart_datalake import SmartDatalake

from .agent import Agent
from .engine import set_pd_engine
from .helpers.cache import Cache
from .skills import skill

__version__ = importlib.metadata.version(__package__ or __name__)


def clear_cache(filename: str = None):
    """Clear the cache"""
    cache = Cache(filename or "cache_db")
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
