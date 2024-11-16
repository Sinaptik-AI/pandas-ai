"""
Databricks Connector to connects you to your Databricks SQL Warhouse on
Azure, AWS and GCP
"""

from typing import Union, Optional, List, Dict, Any
import pandas as pd
from databricks import sql

from pandasai.connectors.base import BaseConnectorConfig
from pandasai_sql.sql import SQLBaseConnectorConfig, SQLConnector


class DatabricksConnectorConfig(SQLBaseConnectorConfig):
    """
    Connector configuration for DataBricks.
    """

    host: str
    token: str
    http_path: str


class DatabricksConnector(SQLConnector):
    """
    Databricks connectors are used to connect to Databricks Data Cloud.
    """

    def __init__(
        self,
        config: Union[DatabricksConnectorConfig, dict],
        **kwargs,
    ):
        """
        Initialize the Databricks connector with the given configuration.

        Args:
            config (ConnectorConfig): The configuration for the Databricks connector.
        """
        config["dialect"] = "databricks"
        if isinstance(config, dict):
            env_vars = {
                "token": "DATABRICKS_TOKEN",
                "database": "DATABRICKS_DATABASE",
                "host": "DATABRICKS_HOST",
                "http_path": "DATABRICKS_HTTP_PATH",
            }
            config = self._populate_config_from_env(config, env_vars)

        super().__init__(config, **kwargs)

    def _load_connector_config(self, config: Union[BaseConnectorConfig, dict]):
        return DatabricksConnectorConfig(**config)

    def _init_connection(self, config: DatabricksConnectorConfig):
        """
        Initialize Database Connection

        Args:
            config (DatabricksConnectorConfig): Configurations to load database
        """
        self._connection = sql.connect(
            server_hostname=config.host,
            http_path=config.http_path,
            access_token=config.token,
        )
        self._cursor = self._connection.cursor()

    def _build_query(
        self,
        limit: Optional[int] = None,
        order: Optional[str] = None,
        where: Optional[List[List[str]]] = None,
    ) -> str:
        """
        Build a SQL query string from the given parameters.

        Args:
            limit (Optional[int]): Maximum number of rows to return
            order (Optional[str]): Column to order by
            where (Optional[List[List[str]]]): List of where conditions. If not provided,
                                             uses conditions from config.

        Returns:
            str: The SQL query string
        """
        query = f"SELECT * FROM {self.config.database}.{self.config.table}"

        # Add WHERE clause
        where_conditions = (
            where if where is not None else getattr(self.config, "where", None)
        )
        if where_conditions:
            conditions = []
            for condition in where_conditions:
                if len(condition) == 3:
                    col, op, val = condition
                    if isinstance(val, str):
                        val = f"'{val}'"
                    conditions.append(f"{col} {op} {val}")
            if conditions:
                query += " WHERE " + " AND ".join(conditions)

        # Add ORDER BY clause
        if order:
            query += f" ORDER BY {order} ASC"

        # Add LIMIT clause
        if limit:
            query += f" LIMIT {limit}"

        return query

    def _execute_query(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> pd.DataFrame:
        """
        Execute a query and return the results as a pandas DataFrame

        Args:
            query (str): The query to execute
            params (Optional[Dict[str, Any]]): Query parameters

        Returns:
            pd.DataFrame: Query results as a DataFrame
        """
        try:
            if params:
                # Replace parameters in query string
                for key, value in params.items():
                    if isinstance(value, str):
                        value = f"'{value}'"
                    query = query.replace(f":{key}", str(value))

            self._cursor.execute(query)
            result = self._cursor.fetchall()

            if not result:
                return pd.DataFrame()

            # Get column names from cursor description
            columns = [desc[0] for desc in self._cursor.description]

            # Convert result to DataFrame
            return pd.DataFrame(result, columns=columns)
        except Exception as e:
            self._cursor = self._connection.cursor()  # Reset cursor on error
            raise e

    def head(self, n: int = 5) -> pd.DataFrame:
        """
        Get the first n rows of the table

        Args:
            n (int, optional): Number of rows to return. Defaults to 5.

        Returns:
            pd.DataFrame: First n rows of the table
        """
        query = self._build_query(limit=n)
        return self._execute_query(query)

    def __repr__(self):
        """
        Return the string representation of the Databricks connector.

        Returns:
        str: The string representation of the Databricks connector.
        """
        return (
            f"<{self.__class__.__name__} dialect={self.config.dialect} "
            f"host={self.config.host} "
            f"database={self.config.database} http_path={self.config.http_path}"
        )

    def equals(self, other):
        if isinstance(other, self.__class__):
            return (
                self.config.dialect,
                self.config.host,
                self.config.http_path,
            ) == (
                other.config.dialect,
                other.config.host,
                other.config.http_path,
            )
        return False

    def close(self):
        """Close the database connection"""
        if hasattr(self, "_cursor") and self._cursor:
            self._cursor.close()
        if hasattr(self, "_connection") and self._connection:
            self._connection.close()
