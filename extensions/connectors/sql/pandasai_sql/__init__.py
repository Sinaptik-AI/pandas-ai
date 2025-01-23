import pandas as pd

from pandasai.data_loader.semantic_layer_schema import (
    SQLConnectionConfig,
    SqliteConnectionConfig,
)


def load_from_mysql(connection_info: SQLConnectionConfig, query: str):
    import pymysql

    conn = pymysql.connect(
        host=connection_info.host,
        user=connection_info.user,
        password=connection_info.password,
        database=connection_info.database,
        port=connection_info.port,
    )
    return pd.read_sql(query, conn)


def load_from_postgres(connection_info: SQLConnectionConfig, query: str):
    import psycopg2

    conn = psycopg2.connect(
        host=connection_info.host,
        user=connection_info.user,
        password=connection_info.password,
        dbname=connection_info.database,
        port=connection_info.port,
    )
    return pd.read_sql(query, conn)


def load_from_sqlite(connection_info: SqliteConnectionConfig, query: str):
    import sqlite3

    conn = sqlite3.connect(connection_info.file_path)
    return pd.read_sql(query, conn)


def load_from_cockroachdb(connection_info: SQLConnectionConfig, query: str):
    import psycopg2

    conn = psycopg2.connect(
        host=connection_info.host,
        user=connection_info.user,
        password=connection_info.password,
        dbname=connection_info.database,
        port=connection_info.port,
    )
    return pd.read_sql(query, conn)


__all__ = [
    "load_from_mysql",
    "load_from_postgres",
    "load_from_sqlite",
    "load_from_cockroachdb",
]
