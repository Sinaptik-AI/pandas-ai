import glob
import os
from typing import Any

import duckdb

from ..constants import CACHE_TOKEN, DEFAULT_FILE_PERMISSIONS
from .path import find_project_root


class Cache:
    """Cache class for caching queries. It is used to cache queries
    to save time and money.

    Args:
        filename (str): filename to store the cache.
    """

    def __init__(self, filename="cache_db_0.11", abs_path=None):
        # Define cache directory and create directory if it does not exist
        if abs_path:
            cache_dir = abs_path
        else:
            try:
                cache_dir = os.path.join(find_project_root(), "cache")
            except ValueError:
                cache_dir = os.path.join(os.getcwd(), "cache")

        os.makedirs(cache_dir, mode=DEFAULT_FILE_PERMISSIONS, exist_ok=True)

        self.filepath = os.path.join(cache_dir, f"{filename}.db")
        self.connection = duckdb.connect(self.filepath)
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS cache (key STRING, value STRING)"
        )

    def versioned_key(self, key: str) -> str:
        return f"{CACHE_TOKEN}-{key}"

    def set(self, key: str, value: str) -> None:
        """Set a key value pair in the cache.

        Args:
            key (str): key to store the value.
            value (str): value to store in the cache.
        """
        self.connection.execute(
            "INSERT INTO cache VALUES (?, ?)", [self.versioned_key(key), value]
        )

    def get(self, key: str) -> str:
        """Get a value from the cache.

        Args:
            key (str): key to get the value from the cache.

        Returns:
            str: value from the cache.
        """
        result = self.connection.execute(
            "SELECT value FROM cache WHERE key=?", [self.versioned_key(key)]
        )
        return row[0] if (row := result.fetchone()) else None

    def delete(self, key: str) -> None:
        """Delete a key value pair from the cache.

        Args:
            key (str): key to delete the value from the cache.
        """
        self.connection.execute(
            "DELETE FROM cache WHERE key=?", [self.versioned_key(key)]
        )

    def close(self) -> None:
        """Close the cache."""
        self.connection.close()

    def clear(self) -> None:
        """Clean the cache."""
        self.connection.execute("DELETE FROM cache")

    def destroy(self) -> None:
        """Destroy the cache."""
        self.connection.close()
        for cache_file in glob.glob(f"{self.filepath}.*"):
            os.remove(cache_file)

    def get_cache_key(self, context: Any) -> str:
        """
        Return the cache key for the current conversation.

        Returns:
            str: The cache key for the current conversation
        """
        cache_key = context.memory.get_conversation()

        # make the cache key unique for each combination of dfs
        for df in context.dfs:
            cache_key += str(df.column_hash)

        return cache_key
