"""
Airtable connectors are used to connect airtable records.
"""

from .base import AirtableConnectorConfig, BaseConnector, BaseConnectorConfig
from typing import Union, Optional
import requests
import pandas as pd
import os
from ..helpers.path import find_project_root
import time
import hashlib
from ..exceptions import InvalidRequestError
from functools import cache, cached_property


class AirtableConnector(BaseConnector):
    """
    Airtable connector to retrieving record data.
    """

    _rows_count: int = None
    _columns_count: int = None
    _instance = None

    def __init__(
        self,
        config: Optional[Union[AirtableConnectorConfig, dict]] = None,
        cache_interval: int = 600,
    ):
        if isinstance(config, dict):
            if "api_key" in config and "base_id" in config and "table" in config:
                config = AirtableConnectorConfig(**config)
            else:
                raise KeyError(
                    "Please specify all api_key,table,base_id properly in config ."
                )

        elif not config:
            airtable_env_vars = {
                "api_key": "AIRTABLE_API_TOKEN",
                "base_id": "AIRTABLE_BASE_ID",
                "table": "AIRTABLE_TABLE_NAME",
            }
            config = AirtableConnectorConfig(
                **self._populate_config_from_env(config, airtable_env_vars)
            )

        self._root_url: str = "https://api.airtable.com/v0/"
        self._cache_interval = cache_interval

        super().__init__(config)

    def _init_connection(self, config: BaseConnectorConfig):
        """
        make connection to database
        """
        config = config.dict()
        url = f"{self._root_url}{config['base_id']}/{config['table']}"
        response = requests.head(
            url=url, headers={"Authorization": f"Bearer {config['api_key']}"}
        )
        if response.status_code == 200:
            self.logger.log(
                """
                Connected to Airtable.
            """
            )
        else:
            raise InvalidRequestError(
                f"""Failed to connect to Airtable. 
                    Status code: {response.status_code}, 
                    message: {response.text}"""
            )

    def _get_cache_path(self, include_additional_filters: bool = False):
        """
        Return the path of the cache file.

        Returns :
            str : The path of the cache file.
        """
        cache_dir = os.path.join(os.getcwd(), "")
        try:
            cache_dir = os.path.join((find_project_root()), "cache")
        except ValueError:
            cache_dir = os.path.join(os.getcwd(), "cache")
        return os.path.join(cache_dir, f"{self._config.table}_data.parquet")

    def _cached(self, include_additional_filters: bool = False):
        """
        Returns the cached Airtable data if it exists and
        is not older than the cache interval.

        Returns :
            DataFrame | None : The cached data if
                it exists and is not older than the cache
                interval, None otherwise.
        """
        cache_path = self._get_cache_path(include_additional_filters)
        if not os.path.exists(cache_path):
            return None

        # If the file is older than 1 day , delete it.
        if os.path.getmtime(cache_path) < time.time() - self._cache_interval:
            if self.logger:
                self.logger.log(f"Deleting expired cached data from {cache_path}")
            os.remove(cache_path)
            return None

        if self.logger:
            self.logger.log(f"Loading cached data from {cache_path}")

        return cache_path

    def _save_cache(self, df):
        """
        Save the given DataFrame to the cache.

        Args:
            df (DataFrame): The DataFrame to save to the cache.
        """
        filename = self._get_cache_path(
            include_additional_filters=self._additional_filters is not None
            and len(self._additional_filters) > 0
        )
        df.to_parquet(filename)

    @property
    def fallback_name(self):
        """
        Returns the fallback table name of the connector.

        Returns :
            str : The fallback table name of the connector.
        """
        return self._config.table

    def execute(self):
        """
        Execute the connector and return the result.

        Returns:
            DataFrameType: The result of the connector.
        """
        if cached := self._cached() or self._cached(include_additional_filters=True):
            return pd.read_parquet(cached)

        if isinstance(self._instance, pd.DataFrame):
            return self._instance
        else:
            self._instance = self._fetch_data()

        return self._instance

    def _build_formula(self):
        """
        Build Airtable query formula for filtering.
        """

        condition_strings = []
        if self._config.where is not None:
            for i in self._config.where:
                filter_query = f"{i[0]}{i[1]}'{i[2]}'"
                condition_strings.append(filter_query)
        return f'AND({",".join(condition_strings)})'

    def _request_api(self, params):
        url = f"{self._root_url}{self._config.base_id}/{self._config.table}"
        return requests.get(
            url=url,
            headers={"Authorization": f"Bearer {self._config.api_key}"},
            params=params,
        )

    def _fetch_data(self):
        """
        Fetches data from the Airtable server via API and converts it to a DataFrame.
        """

        params = {"pageSize": 100, "offset": "0"}

        if self._config.where is not None:
            params["filterByFormula"] = self._build_formula()

        data = []
        while True:
            response = self._request_api(params=params)

            if response.status_code != 200:
                raise InvalidRequestError(
                    f"Failed to connect to Airtable. "
                    f"Status code: {response.status_code}, "
                    f"message: {response.text}"
                )

            res = response.json()
            records = res.get("records", [])
            data.extend({"id": record["id"], **record["fields"]} for record in records)

            if len(records) < 100 or "offset" not in res:
                break

            params["offset"] = res["offset"]

        return pd.DataFrame(data)

    @cache
    def head(self):
        """
        Return the head of the table that
          the connector is connected to.

        Returns :
            DatFrameType: The head of the data source
                 that the connector is connected to .
        """
        data = self._request_api(params={"maxRecords": 5})
        return pd.DataFrame(
            [
                {"id": record["id"], **record["fields"]}
                for record in data.json()["records"]
            ]
        )

    @cached_property
    def rows_count(self):
        """
        Return the number of rows in the data source that the connector is
        connected to.

        Returns:
            int: The number of rows in the data source that the connector is
            connected to.
        """
        if self._rows_count is not None:
            return self._rows_count
        data = self.execute()
        self._rows_count = len(data)
        return self._rows_count

    @cached_property
    def columns_count(self):
        """
        Return the number of columns in the data source that the connector is
        connected to.

        Returns:
            int: The number of columns in the data source that the connector is
            connected to.
        """
        if self._columns_count is not None:
            return self._columns_count
        data = self.head()
        self._columns_count = len(data.columns)
        return self._columns_count

    @property
    def column_hash(self):
        """
        Return the hash code that is unique to the columns of the data source
        that the connector is connected to.

        Returns:
            int: The hash code that is unique to the columns of the data source
            that the connector is connected to.
        """
        if not isinstance(self._instance, pd.DataFrame):
            self._instance = self.execute()
        columns_str = "|".join(self._instance.columns)
        columns_str += "WHERE" + self._build_formula()
        return hashlib.sha256(columns_str.encode("utf-8")).hexdigest()
