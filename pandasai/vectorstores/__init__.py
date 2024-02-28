"""
Vector stores to store data for training purpose
"""

from .bamboo_vectorstore import BambooVectorStore
from .vectorstore import VectorStore

__all__ = ["VectorStore", "BambooVectorStore"]
