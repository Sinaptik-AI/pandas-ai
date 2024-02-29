import hashlib
import os
import time
from typing import Optional, Union

import pandasai.pandas as pd

from ..constants import DEFAULT_FILE_PERMISSIONS
from ..helpers.path import find_project_root
from .base import BaseConnector, BaseConnectorConfig


class YahooFinanceConnectorConfig(BaseConnectorConfig):
    """
    Connector configuration for Yahoo Finance.
    """

    dialect: str = "yahoo_finance"
    host: str = "yahoo.finance.com"
    database: str = "stock_data"
    host: str


class YahooFinanceConnector(BaseConnector):
    """
    Yahoo Finance connector for retrieving stock data.
    """

    _cache_interval: int = 600  # 10 minutes

    def __init__(
        self,
        stock_ticker: Optional[str] = None,
        config: Optional[Union[YahooFinanceConnectorConfig, dict]] = None,
        cache_interval: int = 600,
        **kwargs,
    ):
        if not stock_ticker and not config:
            raise ValueError(
                "You must specify either a stock ticker or a config object."
            )

        try:
            import yfinance
        except ImportError as e:
            raise ImportError(
                "Could not import yfinance python package. "
                "Please install it with `pip install yfinance`."
            ) from e

        if not isinstance(config, YahooFinanceConnectorConfig):
            if not config:
                config = {}

            if stock_ticker:
                config["table"] = stock_ticker

            yahoo_finance_config = YahooFinanceConnectorConfig(**config)
        else:
            yahoo_finance_config = config

        self._cache_interval = cache_interval
        super().__init__(yahoo_finance_config)
        self.ticker = yfinance.Ticker(self.config.table)

    def head(self, n: int = 5) -> pd.DataFrame:
        """
        Return the head of the data source that the connector is connected to.

        Returns:
            DataFrame: The head of the data source that the connector is connected to.
            connected to.
        """
        return self.ticker.history(period=f"{n}d")

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

        return os.path.join(cache_dir, f"{self.config.table}_data.parquet")

    def _get_cache_path(self):
        """
        Return the path of the cache file for Yahoo Finance data.
        """
        try:
            cache_dir = os.path.join((find_project_root()), "cache")
        except ValueError:
            cache_dir = os.path.join(os.getcwd(), "cache")

        os.makedirs(cache_dir, mode=DEFAULT_FILE_PERMISSIONS, exist_ok=True)

        return os.path.join(cache_dir, f"{self.config.table}_data.parquet")

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
            DataFrame: The result of the connector.
        """
        if cached_path := self._cached():
            return pd.read_parquet(cached_path)

        # Use yfinance to retrieve historical stock data
        stock_data = self.ticker.history(period="max")

        # Save the result to the cache
        stock_data.to_parquet(self._get_cache_path())

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
        return self.config.table

    @property
    def pandas_df(self):
        return self.execute()
