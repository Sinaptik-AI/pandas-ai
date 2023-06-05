"""Cache module for caching queries."""

import shelve


class Cache:
    """Cache class for caching queries. It is used to cache queries to avoid save time and money.

    Args:
        filename (str): filename to store the cache.
    """

    def __init__(self, filename="cache"):
        self.filename = filename
        self.cache = shelve.open(filename)

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
