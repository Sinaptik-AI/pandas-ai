# -*- coding: utf-8 -*-
"""
PandasAI is a wrapper around a LLM to make dataframes conversational
"""
import importlib.metadata

from .agent import Agent
from .helpers.cache import Cache
from .skills import skill
from .smart_dataframe import SmartDataframe
from .smart_datalake import SmartDatalake

__version__ = importlib.metadata.version(__package__ or __name__)


def clear_cache(filename: str = None):
    """Clear the cache"""
    cache = Cache(filename or "cache_db")
    cache.clear()


__all__ = [
    "SmartDataframe",
    "SmartDatalake",
    "Agent",
    "clear_cache",
    "skill",
]
