import os
import yaml
import pandas as pd
from datetime import datetime, timedelta
import hashlib
import pymysql
import psycopg2
from .dataframe.base import DataFrame


class DatasetLoader:
    def __init__(self):
        pass

    def load(self, dataset_path: str) -> DataFrame:
        schema_path = os.path.join("datasets", dataset_path, "schema.yaml")
        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"Schema file not found: {schema_path}")

        with open(schema_path, "r") as file:
            schema = yaml.safe_load(file)

        # Check for unsupported database type early
        db_type = schema["source"]["type"]
        if db_type not in ["mysql", "postgres"]:
            raise ValueError(f"Unsupported database type: {db_type}")

        output_format = schema["destination"]["format"]
        update_frequency = schema["update_frequency"]

        cache_file = self._get_cache_file_path(schema, dataset_path)

        # Check if cached file exists and is up-to-date
        if self._is_cache_valid(cache_file, update_frequency):
            return self._read_cache(cache_file, output_format)

        # Load from database
        connection_info = schema["source"]["connection"]
        query = self._generate_query(schema)

        if db_type == "mysql":
            df = self._load_from_mysql(connection_info, query)
        elif db_type == "postgres":
            df = self._load_from_postgres(connection_info, query)

        # Apply transformations
        df = self._apply_transformations(df, schema)

        # Cache the result
        self._cache_data(df, cache_file, output_format)

        return DataFrame(df)

    def _get_cache_file_path(self, schema, dataset_path):
        if "path" in schema["destination"]:
            return os.path.join("datasets", dataset_path, schema["destination"]["path"])

        file_extension = (
            "parquet" if schema["destination"]["format"] == "parquet" else "csv"
        )
        return os.path.join("datasets", dataset_path, f"data.{file_extension}")

    def _is_cache_valid(self, cache_file, update_frequency):
        if os.path.exists(cache_file):
            file_mtime = datetime.fromtimestamp(os.path.getmtime(cache_file))
            if update_frequency == "weekly" and file_mtime > datetime.now() - timedelta(
                weeks=1
            ):
                return True
        return False

    def _read_cache(self, cache_file: str, format: str) -> DataFrame:
        if format == "parquet":
            return DataFrame(pd.read_parquet(cache_file))
        elif format == "csv":
            return DataFrame(pd.read_csv(cache_file))
        else:
            raise ValueError(f"Unsupported cache format: {format}")

    def _cache_data(self, df: pd.DataFrame, cache_file: str, format: str):
        if format == "parquet":
            df.to_parquet(cache_file, index=False)
        elif format == "csv":
            df.to_csv(cache_file, index=False)
        else:
            raise ValueError(f"Unsupported cache format: {format}")

    def _generate_query(self, schema: dict) -> str:
        columns = ", ".join([col["name"] for col in schema["columns"]])
        table_name = schema["source"]["table"]
        query = f"SELECT {columns} FROM {table_name}"

        if "order_by" in schema:
            order_by = schema["order_by"]
            order_by_clause = (
                ", ".join(order_by) if isinstance(order_by, list) else order_by
            )
            query += f" ORDER BY {order_by_clause}"

        if "limit" in schema:
            query += f" LIMIT {schema['limit']}"

        return query

    def _load_from_mysql(self, connection_info, query):
        conn = pymysql.connect(
            host=connection_info["host"],
            user=connection_info["user"],
            password=connection_info["password"],
            database=connection_info["database"],
            port=connection_info["port"],
        )
        return pd.read_sql(query, conn)

    def _load_from_postgres(self, connection_info, query):
        conn = psycopg2.connect(
            host=connection_info["host"],
            user=connection_info["user"],
            password=connection_info["password"],
            dbname=connection_info["database"],
            port=connection_info["port"],
        )
        return pd.read_sql(query, conn)

    def _apply_transformations(self, df, schema):
        for transform in schema.get("transformations", []):
            if transform["type"] == "anonymize":
                df[transform["params"]["column"]] = df[
                    transform["params"]["column"]
                ].apply(lambda x: self._anonymize(x))
            elif transform["type"] == "convert_timezone":
                df[transform["params"]["column"]] = pd.to_datetime(
                    df[transform["params"]["column"]]
                ).dt.tz_convert(transform["params"]["to"])
        return df

    def _anonymize(self, value):
        if not isinstance(value, str) or "@" not in value:
            return value
        try:
            local, domain = value.rsplit("@", 1)
            return f"{hashlib.md5(local.encode()).hexdigest()}@{domain}"
        except ValueError:
            return value
