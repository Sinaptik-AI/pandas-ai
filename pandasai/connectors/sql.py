"""
SQL connectors are used to connect to SQL databases in different dialects.
"""

import re
import os
import pandas as pd
from .base import BaseConnector, SQLConnectorConfig
from .base import BaseConnectorConfig
from sqlalchemy import create_engine, text, select, asc
from sqlalchemy.engine import Connection

from functools import cached_property, cache
import hashlib
from ..helpers.path import find_project_root
from typing import Union
import time


class SQLConnector(BaseConnector):
    """
    SQL connectors are used to connect to SQL databases in different dialects.
    """

    _engine = None
    _connection: Connection = None
    _rows_count: int = None
    _columns_count: int = None
    _cache_interval: int = 600  # 10 minutes

    def __init__(
        self, config: Union[BaseConnectorConfig, dict], cache_interval: int = 600
    ):
        """
        Initialize the SQL connector with the given configuration.

        Args:
            config (ConnectorConfig): The configuration for the SQL connector.
        """
        config = self._load_connector_config(config)
        super().__init__(config)

        if config.dialect is None:
            raise Exception("SQL dialect must be specified")

        self._init_connection(config)

        self._cache_interval = cache_interval

    def _load_connector_config(self, config: Union[BaseConnectorConfig, dict]):
        """
        Loads passed Configuration to object

        Args:
            config (BaseConnectorConfig): Construct config in structure

        Returns:
            config: BaseConenctorConfig
        """
        return SQLConnectorConfig(**config)

    def _init_connection(self, config: SQLConnectorConfig):
        """
        Initialize Database Connection

        Args:
            config (SQLConnectorConfig): Configurations to load database

        """

        if config.driver:
            self._engine = create_engine(
                f"{config.dialect}+{config.driver}://{config.username}:{config.password}"
                f"@{config.host}:{str(config.port)}/{config.database}"
            )
        else:
            self._engine = create_engine(
                f"{config.dialect}://{config.username}:{config.password}@{config.host}"
                f":{str(config.port)}/{config.database}"
            )

        self._connection = self._engine.connect()

    def __del__(self):
        """
        Close the connection to the SQL database.
        """
        self._connection.close()

    def __repr__(self):
        """
        Return the string representation of the SQL connector.

        Returns:
            str: The string representation of the SQL connector.
        """
        return (
            f"<{self.__class__.__name__} dialect={self._config.dialect} "
            f"driver={self._config.driver} host={self._config.host} "
            f"port={str(self._config.port)} database={self._config.database} "
            f"table={self._config.table}>"
        )

    def _validate_column_name(self, column_name):
        regex = r"^[a-zA-Z0-9_]+$"
        if not re.match(regex, column_name):
            raise ValueError("Invalid column name: {}".format(column_name))

    def _build_query(self, limit=None, order=None):
        base_query = select("*").select_from(text(self._config.table))
        valid_operators = ["=", ">", "<", ">=", "<=", "LIKE", "!=", "IN", "NOT IN"]

        if self._config.where or self._additional_filters:
            # conditions is the list of wher + additional filters
            conditions = []
            if self._config.where:
                conditions += self._config.where
            if self._additional_filters:
                conditions += self._additional_filters

            query_params = {}
            condition_strings = []

            for i, condition in enumerate(conditions):
                if len(condition) == 3:
                    column_name, operator, value = condition
                    if operator in valid_operators:
                        self._validate_column_name(column_name)

                        condition_strings.append(f"{column_name} {operator} :value_{i}")
                        query_params[f"value_{i}"] = value

            if condition_strings:
                where_clause = " AND ".join(condition_strings)
                base_query = base_query.where(
                    text(where_clause).bindparams(**query_params)
                )

        if order:
            base_query = base_query.order_by(asc(text(order)))

        if limit:
            base_query = base_query.limit(limit)

        return base_query

    @cache
    def head(self):
        """
        Return the head of the data source that the connector is connected to.
        This information is passed to the LLM to provide the schema of the data source.

        Returns:
            DataFrame: The head of the data source.
        """

        if self.logger:
            self.logger.log(
                f"Getting head of {self._config.table} "
                f"using dialect {self._config.dialect}"
            )

        # Run a SQL query to get all the columns names and 5 random rows
        query = self._build_query(limit=5, order="RAND()")

        # Return the head of the data source
        return pd.read_sql(query, self._connection)

    def _get_cache_path(self, include_additional_filters: bool = False):
        """
        Return the path of the cache file.

        Args:
            include_additional_filters (bool, optional): Whether to include the
                additional filters in when calling `_get_column_hash()`.
                Defaults to False.

        Returns:
            str: The path of the cache file.
        """
        try:
            cache_dir = os.path.join((find_project_root()), "cache")
        except ValueError:
            cache_dir = os.path.join(os.getcwd(), "cache")

        os.makedirs(cache_dir, mode=0o777, exist_ok=True)

        filename = (
            self._get_column_hash(include_additional_filters=include_additional_filters)
            + ".parquet"
        )
        path = os.path.join(cache_dir, filename)

        return path

    def _cached(self, include_additional_filters: bool = False) -> Union[str, bool]:
        """
        Return the cached data if it exists and is not older than the cache interval.

        Args:
            include_additional_filters (bool, optional): Whether to include the
                additional filters in when calling `_get_column_hash()`.
                Defaults to False.

        Returns:
            DataFrame|bool: The name of the file containing cached data if it exists
                and is not older than the cache interval, False otherwise.
        """
        filename = self._get_cache_path(
            include_additional_filters=include_additional_filters
        )
        if not os.path.exists(filename):
            return False

        # If the file is older than 1 day, delete it
        if os.path.getmtime(filename) < time.time() - self._cache_interval:
            if self.logger:
                self.logger.log(f"Deleting expired cached data from {filename}")
            os.remove(filename)
            return False

        if self.logger:
            self.logger.log(f"Loading cached data from {filename}")

        return filename

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

    def execute(self):
        """
        Execute the SQL query and return the result.

        Returns:
            DataFrame: The result of the SQL query.
        """

        # try to load the generic cache first, then the cache with additional
        # filters as a fallback
        cached = self._cached() or self._cached(include_additional_filters=True)
        if cached:
            return pd.read_parquet(cached)

        if self.logger:
            self.logger.log(
                f"Loading the table {self._config.table} "
                f"using dialect {self._config.dialect}"
            )

        # Run a SQL query to get all the results
        query = self._build_query()

        # Get the result of the query
        result = pd.read_sql(query, self._connection)

        # Save the result to the cache
        self._save_cache(result)

        # Return the result
        return result

    @cached_property
    def rows_count(self):
        """
        Return the number of rows in the SQL table.

        Returns:
            int: The number of rows in the SQL table.
        """

        if self._rows_count is not None:
            return self._rows_count

        if self.logger:
            self.logger.log(
                "Getting the number of rows in the table "
                f"{self._config.table} using dialect "
                f"{self._config.dialect}"
            )

        # Run a SQL query to get the number of rows
        query = select(text("COUNT(*)")).select_from(text(self._config.table))

        # Return the number of rows
        self._rows_count = self._connection.execute(query).fetchone()[0]
        return self._rows_count

    @cached_property
    def columns_count(self):
        """
        Return the number of columns in the SQL table.

        Returns:
            int: The number of columns in the SQL table.
        """

        if self._columns_count is not None:
            return self._columns_count

        if self.logger:
            self.logger.log(
                "Getting the number of columns in the table "
                f"{self._config.table} using dialect "
                f"{self._config.dialect}"
            )

        self._columns_count = len(self.head().columns)
        return self._columns_count

    def _get_column_hash(self, include_additional_filters: bool = False):
        """
        Return the hash of the SQL table columns.

        Args:
            include_additional_filters (bool, optional): Whether to include the
                additional filters in the hash. Defaults to False.

        Returns:
            str: The hash of the SQL table columns.
        """

        # Return the hash of the columns and the where clause
        columns_str = "".join(self.head().columns)
        if (
            self._config.where
            or include_additional_filters
            and self._additional_filters is not None
        ):
            columns_str += "WHERE"
        if self._config.where:
            # where clause is a list of lists
            for condition in self._config.where:
                columns_str += f"{condition[0]} {condition[1]} {condition[2]}"
        if include_additional_filters and self._additional_filters:
            for condition in self._additional_filters:
                columns_str += f"{condition[0]} {condition[1]} {condition[2]}"

        hash_object = hashlib.sha256(columns_str.encode())
        return hash_object.hexdigest()

    @cached_property
    def column_hash(self):
        """
        Return the hash of the SQL table columns.

        Returns:
            str: The hash of the SQL table columns.
        """
        return self._get_column_hash()

    @property
    def fallback_name(self):
        return self._config.table


class MySQLConnector(SQLConnector):
    """
    MySQL connectors are used to connect to MySQL databases.
    """

    def __init__(self, config: Union[SQLConnectorConfig, dict]):
        """
        Initialize the MySQL connector with the given configuration.

        Args:
            config (ConnectorConfig): The configuration for the MySQL connector.
        """
        config["dialect"] = "mysql"
        config["driver"] = "pymysql"

        if isinstance(config, dict):
            mysql_env_vars = {
                "host": "MYSQL_HOST",
                "port": "MYSQL_PORT",
                "database": "MYSQL_DATABASE",
                "username": "MYSQL_USERNAME",
                "password": "MYSQL_PASSWORD",
            }
            config = self._populate_config_from_env(config, mysql_env_vars)

        super().__init__(config)


class PostgreSQLConnector(SQLConnector):
    """
    PostgreSQL connectors are used to connect to PostgreSQL databases.
    """

    def __init__(self, config: Union[SQLConnectorConfig, dict]):
        """
        Initialize the PostgreSQL connector with the given configuration.

        Args:
            config (ConnectorConfig): The configuration for the PostgreSQL connector.
        """
        config["dialect"] = "postgresql"
        config["driver"] = "psycopg2"

        if isinstance(config, dict):
            postgresql_env_vars = {
                "host": "POSTGRESQL_HOST",
                "port": "POSTGRESQL_PORT",
                "database": "POSTGRESQL_DATABASE",
                "username": "POSTGRESQL_USERNAME",
                "password": "POSTGRESQL_PASSWORD",
            }
            config = self._populate_config_from_env(config, postgresql_env_vars)

        super().__init__(config)

    @cache
    def head(self):
        """
        Return the head of the data source that the connector is connected to.
        This information is passed to the LLM to provide the schema of the data source.

        Returns:
            DataFrame: The head of the data source.
        """

        if self.logger:
            self.logger.log(
                f"Getting head of {self._config.table} "
                f"using dialect {self._config.dialect}"
            )

        # Run a SQL query to get all the columns names and 5 random rows
        query = self._build_query(limit=5, order="RANDOM()")

        # Return the head of the data source
        return pd.read_sql(query, self._connection)
