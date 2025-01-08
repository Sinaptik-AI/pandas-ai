import pandas as pd
from snowflake import connector


def load_from_snowflake(connection_info, query):
    conn = connector.connect(
        account=connection_info["account"],
        user=connection_info["user"],
        password=connection_info["password"],
        warehouse=connection_info["warehouse"],
        database=connection_info["database"],
        schema=connection_info.get("schema"),
        role=connection_info.get("role"),
    )
    return pd.read_sql(query, conn)


__all__ = ["load_from_snowflake"]
