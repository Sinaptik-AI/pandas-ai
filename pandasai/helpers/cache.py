import os
import glob
import duckdb
from .path import find_project_root


class Cache:
    """Cache class for caching queries. It is used to cache queries
    to save time and money.

    Args:
        filename (str): filename to store the cache.
    """

    def __init__(self, filename="cache_db", abs_path=None):
        # Define cache directory and create directory if it does not exist
        if abs_path:
            cache_dir = abs_path
        else:
            try:
                cache_dir = os.path.join(find_project_root(), "cache")
            except ValueError:
                cache_dir = os.path.join(os.getcwd(), "cache")

        os.makedirs(cache_dir, mode=0o777, exist_ok=True)

        self.filepath = os.path.join(cache_dir, filename + ".db")
        self.connection = duckdb.connect(self.filepath)
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS cache (key STRING, value STRING)"
        )

    def set(self, key: str, value: str) -> None:
        """Set a key value pair in the cache.

        Args:
            key (str): key to store the value.
            value (str): value to store in the cache.
        """
        self.connection.execute("INSERT INTO cache VALUES (?, ?)", [key, value])

    def get(self, key: str) -> str:
        """Get a value from the cache.

        Args:
            key (str): key to get the value from the cache.

        Returns:
            str: value from the cache.
        """
        result = self.connection.execute("SELECT value FROM cache WHERE key=?", [key])
        row = result.fetchone()
        if row:
            return row[0]
        else:
            return None

    def delete(self, key: str) -> None:
        """Delete a key value pair from the cache.

        Args:
            key (str): key to delete the value from the cache.
        """
        self.connection.execute("DELETE FROM cache WHERE key=?", [key])

    def close(self) -> None:
        """Close the cache."""
        self.connection.close()

    def clear(self) -> None:
        """Clean the cache."""
        self.connection.execute("DELETE FROM cache")

    def destroy(self) -> None:
        """Destroy the cache."""
        self.connection.close()
        for cache_file in glob.glob(self.filepath + ".*"):
            os.remove(cache_file)
