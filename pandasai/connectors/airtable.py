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


class AirtableConnector(BaseConnector):
    """
    Airtable connector to retrieving record data.
    """

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

    def _cached(self):
        """
        Returns the cached Airtable data if it exists and
        is not older than the cache interval.

        Returns :
            DataFrame | None : The cached data if
                it exists and is not older than the cache
                interval, None otherwise.
        """
        cache_path = self._get_cache_path()
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
        return self.fetch_data()

    def build_formula(self):
        """
        Build Airtable query formula for filtering.
        """

        condition_strings = []
        for i in self._config.where:
            filter_query = f"{i[0]}{i[1]}'{i[2]}'"
            condition_strings.append(filter_query)
        filter_formula = f'AND({",".join(condition_strings)})'
        return filter_formula

    def fetch_data(self):
        """
        Feteches data from airtable server through
            API and converts it to DataFrame.
        """
        url = f"{self._root_url}{self._config.base_id}/{self._config.table}"
        params = {}

        if self._config.where:
            params["filterByFormula"] = self.build_formula()
        response = requests.get(
            url=url,
            headers={"Authorization": f"Bearer {self._config.api_key}"},
            params=params,
        )
        if response.status_code == 200:
            data = response.json()
            data = self.preprocess(data=data)
            self._save_cache(data)
        else:
            raise InvalidRequestError(
                f"""Failed to connect to Airtable. 
                    Status code: {response.status_code}, 
                    message: {response.text}"""
            )
        return data

    def preprocess(self, data):
        """
        Preprocesses Json response data
        To prepare dataframe correctly.
        """
        records = [
            {"id": record["id"], **record["fields"]} for record in data["records"]
        ]

        df = pd.DataFrame(records)
        return df

    def head(self):
        """
        Return the head of the table that
          the connector is connected to.

        Returns :
            DatFrameType: The head of the data source
                 that the conector is connected to .
        """
        return self.fetch_data().head()

    @property
    def rows_count(self):
        """
        Return the number of rows in the data source that the connector is
        connected to.

        Returns:
            int: The number of rows in the data source that the connector is
            connected to.
        """
        data = self.execute()
        return len(data)

    @property
    def columns_count(self):
        """
        Return the number of columns in the data source that the connector is
        connected to.

        Returns:
            int: The number of columns in the data source that the connector is
            connected to.
        """
        data = self.execute()
        return len(data.columns)

    @property
    def column_hash(self):
        """
        Return the hash code that is unique to the columns of the data source
        that the connector is connected to.

        Returns:
            int: The hash code that is unique to the columns of the data source
            that the connector is connected to.
        """
        data = self.execute()
        columns_str = "|".join(data.columns)
        return hashlib.sha256(columns_str.encode("utf-8")).hexdigest()
