import os
import pandas as pd
from .base import ConnectorConfig, BaseConnector
import time
from ..helpers.path import find_project_root
import hashlib


class YahooFinanceConnector(BaseConnector):
    """
    Yahoo Finance connector for retrieving stock data.
    """

    _cache_interval: int = 600  # 10 minutes

    def __init__(self, stock_ticker, where=None, cache_interval: int = 600):
        try:
            import yfinance
        except ImportError:
            raise ImportError(
                "Could not import yfinance python package. "
                "Please install it with `pip install yfinance`."
            )
        yahoo_finance_config = ConnectorConfig(
            dialect="yahoo_finance",
            username="",
            password="",
            host="yahoo.finance.com",
            port=443,
            database="stock_data",
            table=stock_ticker,
            where=where,
        )
        self._cache_interval = cache_interval
        super().__init__(yahoo_finance_config)
        self.ticker = yfinance.Ticker(self._config.table)

    def head(self):
        """
        Return the head of the data source that the connector is connected to.

        Returns:
            DataFrameType: The head of the data source that the connector is
            connected to.
        """
        head_data = self.ticker.history(period="5d")
        return head_data

    def _get_cache_path(self, include_additional_filters: bool = False):
        """
        Return the path of the cache file.

        Returns:
            str: The path of the cache file.
        """
        cache_dir = os.path.join(os.getcwd(), "")
        try:
            cache_dir = os.path.join((find_project_root()), "cache")
        except ValueError:
            cache_dir = os.path.join(os.getcwd(), "cache")

        return os.path.join(cache_dir, f"{self._config.table}_data.csv")

    def _get_cache_path(self):
        """
        Return the path of the cache file for Yahoo Finance data.
        """
        try:
            cache_dir = os.path.join((find_project_root()), "cache")
        except ValueError:
            cache_dir = os.path.join(os.getcwd(), "cache")

        os.makedirs(cache_dir, mode=0o777, exist_ok=True)

        return os.path.join(cache_dir, f"{self._config.table}_data.csv")

    def _cached(self):
        """
        Return the cached Yahoo Finance data if it exists and is not older than the
        cache interval.

        Returns:
            DataFrame|None: The cached data if it exists and is not older than the cache
            interval, None otherwise.
        """
        cache_path = self._get_cache_path()
        if not os.path.exists(cache_path):
            return None

        # If the file is older than 1 day, delete it
        if os.path.getmtime(cache_path) < time.time() - self._cache_interval:
            if self.logger:
                self.logger.log(f"Deleting expired cached data from {cache_path}")
            os.remove(cache_path)
            return None

        if self.logger:
            self.logger.log(f"Loading cached data from {cache_path}")

        return cache_path

    def execute(self):
        """
        Execute the connector and return the result.

        Returns:
            DataFrameType: The result of the connector.
        """
        cached_path = self._cached()
        if cached_path:
            return pd.read_csv(cached_path)

        # Use yfinance to retrieve historical stock data
        stock_data = self.ticker.history(period="max")

        # Save the result to the cache
        stock_data.to_csv(self._get_cache_path(), index=False)

        return stock_data

    @property
    def rows_count(self):
        """
        Return the number of rows in the data source that the connector is
        connected to.

        Returns:
            int: The number of rows in the data source that the connector is
            connected to.
        """
        stock_data = self.execute()
        return len(stock_data)

    @property
    def columns_count(self):
        """
        Return the number of columns in the data source that the connector is
        connected to.

        Returns:
            int: The number of columns in the data source that the connector is
            connected to.
        """
        stock_data = self.execute()
        return len(stock_data.columns)

    @property
    def column_hash(self):
        """
        Return the hash code that is unique to the columns of the data source
        that the connector is connected to.

        Returns:
            int: The hash code that is unique to the columns of the data source
            that the connector is connected to.
        """
        stock_data = self.execute()
        columns_str = "|".join(stock_data.columns)
        return hashlib.sha256(columns_str.encode("utf-8")).hexdigest()

    @property
    def fallback_name(self):
        """
        Return the fallback name of the connector.

        Returns:
            str: The fallback name of the connector.
        """
        return self._config.table
