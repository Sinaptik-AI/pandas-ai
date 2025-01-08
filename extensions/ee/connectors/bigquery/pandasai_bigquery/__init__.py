from google.cloud import bigquery
import pandas as pd


def load_from_bigquery(connection_info, query):
    client = bigquery.Client(
        project=connection_info["project_id"],
        credentials=connection_info.get("credentials"),
    )

    query_job = client.query(query)
    return pd.DataFrame(query_job.result())


__all__ = ["load_from_bigquery"]
