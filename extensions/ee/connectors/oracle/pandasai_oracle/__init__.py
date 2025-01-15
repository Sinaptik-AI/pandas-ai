import cx_Oracle
import pandas as pd


def load_from_oracle(connection_info, query):
    dsn = cx_Oracle.makedsn(
        connection_info["host"],
        connection_info["port"],
        service_name=connection_info.get("service_name"),
        sid=connection_info.get("sid"),
    )
    conn = cx_Oracle.connect(
        user=connection_info["user"], password=connection_info["password"], dsn=dsn
    )
    return pd.read_sql(query, conn)


__all__ = ["load_from_oracle"]
