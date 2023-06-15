"""Cache module for caching queries."""
import glob
import os
import shelve
from pathlib import Path


class Cache:
    """Cache class for caching queries. It is used to cache queries
    to save time and money.

    Args:
        filename (str): filename to store the cache.
    """

    def __init__(self, filename="cache"):
        # define cache directory and create directory if it does not exist
        cache_dir = os.path.join(Path.cwd(), "cache")
        os.makedirs(cache_dir, mode=0o777, exist_ok=True)

        self.filepath = os.path.join(cache_dir, filename)
        self.cache = shelve.open(self.filepath)

    def set(self, key: str, value: str) -> None:
        """Set a key value pair in the cache.

        Args:
            key (str): key to store the value.
            value (str): value to store in the cache.
        """

        self.cache[key] = value

    def get(self, key: str) -> str:
        """Get a value from the cache.

        Args:
            key (str): key to get the value from the cache.

        Returns:
            str: value from the cache.
        """

        return self.cache.get(key)

    def delete(self, key: str) -> None:
        """Delete a key value pair from the cache.

        Args:
            key (str): key to delete the value from the cache.
        """

        if key in self.cache:
            del self.cache[key]

    def close(self) -> None:
        """Close the cache."""

        self.cache.close()

    def clear(self) -> None:
        """Clean the cache."""

        self.cache.clear()

    def destroy(self) -> None:
        """Destroy the cache."""
        self.cache.close()
        for cache_file in glob.glob(self.filepath + ".*"):
            os.remove(cache_file)
