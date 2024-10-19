from functools import cache
import pandas as pd
from typing import Union
from pandasai_sql import SQLConnector, SQLConnectorConfig


class OracleConnector(SQLConnector):
    """
    Oracle connectors are used to connect to Oracle databases.
    """

    def __init__(
        self,
        config: Union[SQLConnectorConfig, dict],
        **kwargs,
    ):
        """
        Initialize the Oracle connector with the given configuration.

        Args:
            config (ConnectorConfig): The configuration for the Oracle connector.
        """
        config["dialect"] = "oracle"
        config["driver"] = "cx_oracle"

        if isinstance(config, dict):
            oracle_env_vars = {
                "host": "ORACLE_HOST",
                "port": "ORACLE_PORT",
                "database": "ORACLE_DATABASE",
                "username": "ORACLE_USERNAME",
                "password": "ORACLE_PASSWORD",
            }
            config = self._populate_config_from_env(config, oracle_env_vars)

        super().__init__(config, **kwargs)

    @cache
    def head(self, n: int = 5) -> pd.DataFrame:
        """
        Return the head of the data source that the connector is connected to.
        This information is passed to the LLM to provide the schema of the data source.

        Returns:
            DataFrame: The head of the data source.
        """

        if self.logger:
            self.logger.log(
                f"Getting head of {self.config.table} "
                f"using dialect {self.config.dialect}"
            )

        # Run a SQL query to get all the columns names and 5 random rows
        query = self._build_query(limit=n, order="dbms_random.value")

        # Return the head of the data source
        return pd.read_sql(query, self._connection)

    @property
    def cs_table_name(self):
        return f'"{self.config.table}"'
