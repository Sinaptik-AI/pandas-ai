import pandas as pd


def load_from_mysql(connection_info, query):
    import pymysql

    conn = pymysql.connect(
        host=connection_info["host"],
        user=connection_info["user"],
        password=connection_info["password"],
        database=connection_info["database"],
        port=connection_info["port"],
    )
    return pd.read_sql(query, conn)


def load_from_postgres(connection_info, query):
    import psycopg2

    conn = psycopg2.connect(
        host=connection_info["host"],
        user=connection_info["user"],
        password=connection_info["password"],
        dbname=connection_info["database"],
        port=connection_info["port"],
    )
    return pd.read_sql(query, conn)


def load_from_sqlite(connection_info, query):
    import sqlite3

    conn = sqlite3.connect(connection_info["database"])
    return pd.read_sql(query, conn)


def load_from_cockroachdb(connection_info, query):
    import psycopg2

    conn = psycopg2.connect(
        host=connection_info["host"],
        user=connection_info["user"],
        password=connection_info["password"],
        dbname=connection_info["database"],
        port=connection_info["port"],
    )
    return pd.read_sql(query, conn)


__all__ = [
    "SQLConnector",
    "SqliteConnector",
    "SQLConnectorConfig",
    "load_from_mysql",
    "load_from_postgres",
    "load_from_sqlite",
    "load_from_cockroach",
]
