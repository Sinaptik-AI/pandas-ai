from .databricks import DatabricksConnector
import pandas as pd
from databricks import sql


def load_from_databricks(connection_info, query):
    connection = sql.connect(
        server_hostname=connection_info["server_hostname"],
        http_path=connection_info["http_path"],
        access_token=connection_info["access_token"],
    )

    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]

    cursor.close()
    connection.close()

    return pd.DataFrame(result, columns=columns)


__all__ = ["DatabricksConnector", "load_from_databricks"]
