"""
SQL connectors are used to connect to SQL databases in different dialects.
"""

import os
import pandas as pd
from .base import BaseConnector
from sqlalchemy import create_engine, sql
from pydantic import BaseModel
from typing import Optional
from functools import cached_property, cache
import hashlib
from ..helpers.path import find_project_root
import time


class SQLConfig(BaseModel):
    """
    SQL configuration.
    """

    dialect: Optional[str] = None
    driver: Optional[str] = None
    username: str
    password: str
    host: str
    port: str
    database: str
    table: str
    where: dict = None


class SQLConnector(BaseConnector):
    """
    SQL connectors are used to connect to SQL databases in different dialects.
    """

    _engine = None
    _connection: int = None
    _rows_count: int = None
    _columns_count: int = None
    _cache_interval: int = 600  # 10 minutes

    def __init__(self, config: SQLConfig, cache_interval: int = 600):
        """
        Initialize the SQL connector with the given configuration.

        Args:
            config (SQLConfig): The configuration for the SQL connector.
        """
        config = SQLConfig(**config)
        super().__init__(config)

        if config.dialect is None:
            raise Exception("SQL dialect must be specified")

        if config.driver:
            self._engine = create_engine(
                f"{config.dialect}+{config.driver}://{config.username}:{config.password}"
                f"@{config.host}:{config.port}/{config.database}"
            )
        else:
            self._engine = create_engine(
                f"{config.dialect}://{config.username}:{config.password}@{config.host}"
                f":{config.port}/{config.database}"
            )
        self._connection = self._engine.connect()
        self._cache_interval = cache_interval

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
            f"driver={self._config.driver} username={self._config.username} "
            f"password={self._config.password} host={self._config.host} "
            f"port={self._config.port} database={self._config.database} "
            f"table={self._config.table}>"
        )

    def _build_query(self, limit: int = None, order: str = None):
        """
        Build the SQL query that will be executed.

        Args:
            limit (int, optional): The number of rows to return. Defaults to None.

        Returns:
            str: The SQL query that will be executed.
        """

        # Run a SQL query to get all the columns names and 5 random rows
        query = f"SELECT * FROM {self._config.table}"
        if self._config.where:
            query += " WHERE "

            conditions = []
            for key, value in self._config.where.items():
                conditions.append(f"{key} = '{value}'")

            query += " AND ".join(conditions)
        if order:
            query += f" ORDER BY {order}"
        if limit:
            query += f" LIMIT {limit}"

        # Return the query
        return sql.text(query)

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

    def _get_cache_path(self):
        """
        Return the path of the cache file.

        Returns:
            str: The path of the cache file.
        """
        try:
            cache_dir = os.path.join((find_project_root()), "cache")
        except ValueError:
            cache_dir = os.path.join(os.getcwd(), "cache")

        os.makedirs(cache_dir, mode=0o777, exist_ok=True)

        filename = self.column_hash + ".csv"
        path = os.path.join(cache_dir, filename)

        return path

    def _cached(self):
        """
        Return the cached data if it exists and is not older than the cache interval.

        Returns:
            DataFrame|bool: The cached data if it exists and is not older than
            the cache interval, False otherwise.
        """
        filename = self._get_cache_path()
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

        return pd.read_csv(filename)

    def _save_cache(self, df):
        """
        Save the given DataFrame to the cache.

        Args:
            df (DataFrame): The DataFrame to save to the cache.
        """

        filename = self._get_cache_path()
        df.to_csv(filename, index=False)

    @cache
    def execute(self):
        """
        Execute the SQL query and return the result.

        Returns:
            DataFrame: The result of the SQL query.
        """

        cached = self._cached()
        if cached is not False:
            return cached

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
        query = sql.text(f"SELECT COUNT(*) FROM {self._config.table}")

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

        # Run a SQL query to get the number of columns
        query = sql.text(
            "SELECT COUNT(*) FROM information_schema.columns "
            f"WHERE table_name = '{self._config.table}'"
        )

        # Return the number of columns
        self._columns_count = self._connection.execute(query).fetchone()[0]
        return self._columns_count

    @cached_property
    def column_hash(self):
        """
        Return the hash of the SQL table columns.

        Returns:
            str: The hash of the SQL table columns.
        """

        # Return the hash of the columns
        columns_str = "".join(self.head().columns)
        hash_object = hashlib.sha256(columns_str.encode())
        return hash_object.hexdigest()

    @property
    def fallback_name(self):
        return self._config.table


class MySQLConnector(SQLConnector):
    """
    MySQL connectors are used to connect to MySQL databases.
    """

    def __init__(self, config: SQLConfig):
        """
        Initialize the MySQL connector with the given configuration.

        Args:
            config (SQLConfig): The configuration for the MySQL connector.
        """
        config["dialect"] = "mysql"
        config["driver"] = "pymysql"

        if "host" not in config and os.getenv("MYSQL_HOST"):
            config["host"] = os.getenv("MYSQL_HOST")
        if "port" not in config and os.getenv("MYSQL_PORT"):
            config["port"] = os.getenv("MYSQL_PORT")
        if "database" not in config and os.getenv("MYSQL_DATABASE"):
            config["database"] = os.getenv("MYSQL_DATABASE")
        if "username" not in config and os.getenv("MYSQL_USERNAME"):
            config["username"] = os.getenv("MYSQL_USERNAME")
        if "password" not in config and os.getenv("MYSQL_PASSWORD"):
            config["password"] = os.getenv("MYSQL_PASSWORD")

        super().__init__(config)


class PostgreSQLConnector(SQLConnector):
    """
    PostgreSQL connectors are used to connect to PostgreSQL databases.
    """

    def __init__(self, config: SQLConfig):
        """
        Initialize the PostgreSQL connector with the given configuration.

        Args:
            config (SQLConfig): The configuration for the PostgreSQL connector.
        """
        config["dialect"] = "postgresql"
        config["driver"] = "psycopg2"

        if "host" not in config and os.getenv("POSTGRESQL_HOST"):
            config["host"] = os.getenv("POSTGRESQL_HOST")
        if "port" not in config and os.getenv("POSTGRESQL_PORT"):
            config["port"] = os.getenv("POSTGRESQL_PORT")
        if "database" not in config and os.getenv("POSTGRESQL_DATABASE"):
            config["database"] = os.getenv("POSTGRESQL_DATABASE")
        if "username" not in config and os.getenv("POSTGRESQL_USERNAME"):
            config["username"] = os.getenv("POSTGRESQL_USERNAME")
        if "password" not in config and os.getenv("POSTGRESQL_PASSWORD"):
            config["password"] = os.getenv("POSTGRESQL_PASSWORD")

        super().__init__(config)
