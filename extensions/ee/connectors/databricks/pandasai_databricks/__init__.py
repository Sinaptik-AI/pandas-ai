import pandas as pd
from databricks import sql


def load_from_databricks(config):
    """
    Load data from Databricks SQL into a pandas DataFrame.

    Args:
        config (dict): Configuration dictionary containing:
            - host: Databricks server hostname
            - http_path: HTTP path for the SQL warehouse
            - token: Access token for authentication
            - database: (optional) Database name
            - table: (optional) Table name
            - query: (optional) Custom SQL query

    Returns:
        pd.DataFrame: DataFrame containing the query results
    """
    connection = sql.connect(
        server_hostname=config["host"],
        http_path=config["http_path"],
        access_token=config["token"],
    )

    cursor = connection.cursor()

    try:
        if "query" in config:
            query = config["query"]
        elif "table" in config:
            query = f"SELECT * FROM {config['database']}.{config['table']}"
        else:
            raise ValueError("Either 'query' or 'table' must be provided in config")

        cursor.execute(query)
        result = cursor.fetchall()

        if not result:
            return pd.DataFrame()

        columns = [desc[0] for desc in cursor.description]
        return pd.DataFrame(result, columns=columns)
    finally:
        cursor.close()
        connection.close()


__all__ = ["load_from_databricks"]
