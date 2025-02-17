from unittest.mock import MagicMock, mock_open, patch

import pytest
import sqlglot

from pandasai.data_loader.semantic_layer_schema import SemanticLayerSchema
from pandasai.query_builders import LocalQueryBuilder
from pandasai.query_builders.base_query_builder import BaseQueryBuilder
from pandasai.query_builders.sql_query_builder import SqlQueryBuilder


class TestQueryBuilder:
    @pytest.fixture
    def mysql_schema(self):
        raw_schema = {
            "name": "Users",
            "update_frequency": "weekly",
            "columns": [
                {
                    "name": "email",
                    "type": "string",
                    "description": "User's email address",
                },
                {
                    "name": "first_name",
                    "type": "string",
                    "description": "User's first name",
                },
                {
                    "name": "timestamp",
                    "type": "datetime",
                    "description": "Timestamp of the record",
                },
            ],
            "order_by": ["created_at DESC"],
            "limit": 100,
            "transformations": [
                {"type": "anonymize", "params": {"column": "email"}},
                {
                    "type": "convert_timezone",
                    "params": {"column": "timestamp", "to": "UTC"},
                },
            ],
            "source": {
                "type": "mysql",
                "connection": {
                    "host": "localhost",
                    "port": 3306,
                    "database": "test_db",
                    "user": "test_user",
                    "password": "test_password",
                },
                "table": "users",
            },
        }
        return SemanticLayerSchema(**raw_schema)

    def test_build_query_csv(self, sample_schema):
        with patch(
            "pandasai.query_builders.local_query_builder.ConfigManager.get"
        ) as mock_config_get:
            # Mock the return of `ConfigManager.get()`
            mock_config = MagicMock()
            mock_config.file_manager.abs_path.return_value = "/mocked/absolute/path"
            mock_config_get.return_value = mock_config
            query_builder = LocalQueryBuilder(sample_schema, "test/test")
            query = query_builder.build_query()
            expected_query = """SELECT
  email,
  first_name,
  timestamp
FROM READ_CSV('/mocked/absolute/path')
ORDER BY
  created_at DESC
LIMIT 100"""
            assert query == expected_query

    def test_build_query_parquet(self, sample_schema):
        sample_schema.source.type = "parquet"
        with patch(
            "pandasai.query_builders.local_query_builder.ConfigManager.get"
        ) as mock_config_get:
            # Mock the return of `ConfigManager.get()`
            mock_config = MagicMock()
            mock_config.file_manager.abs_path.return_value = "/mocked/absolute/path"
            mock_config_get.return_value = mock_config
            query_builder = LocalQueryBuilder(sample_schema, "test/test")
            query = query_builder.build_query()
            expected_query = """SELECT
  email,
  first_name,
  timestamp
FROM READ_PARQUET('/mocked/absolute/path')
ORDER BY
  created_at DESC
LIMIT 100"""
            assert query == expected_query

    def test_build_query(self, mysql_schema):
        query_builder = SqlQueryBuilder(mysql_schema)
        query = query_builder.build_query()
        expected_query = """SELECT
  email,
  first_name,
  timestamp
FROM users
ORDER BY
  created_at DESC
LIMIT 100"""
        assert query == expected_query

    def test_build_query_without_order_by(self, mysql_schema):
        mysql_schema.order_by = None
        query_builder = SqlQueryBuilder(mysql_schema)
        query = query_builder.build_query()
        expected_query = """SELECT
  email,
  first_name,
  timestamp
FROM users
LIMIT 100"""
        assert query == expected_query

    def test_build_query_without_limit(self, mysql_schema):
        mysql_schema.limit = None
        query_builder = SqlQueryBuilder(mysql_schema)
        query = query_builder.build_query()
        expected_query = """SELECT
  email,
  first_name,
  timestamp
FROM users
ORDER BY
  created_at DESC"""
        assert query == expected_query

    def test_build_query_with_multiple_order_by(self, mysql_schema):
        mysql_schema.order_by = ["created_at DESC", "email ASC"]
        query_builder = SqlQueryBuilder(mysql_schema)
        query = query_builder.build_query()
        expected_query = """SELECT
  email,
  first_name,
  timestamp
FROM users
ORDER BY
  created_at DESC,
  email ASC
LIMIT 100"""
        assert query == expected_query

    def test_table_name_injection(self, mysql_schema):
        mysql_schema.name = "users; DROP TABLE users;"
        query_builder = BaseQueryBuilder(mysql_schema)
        query = query_builder.build_query()
        assert (
            query
            == """SELECT
  email,
  first_name,
  timestamp
FROM "users; DROP TABLE users;"
ORDER BY
  created_at DESC
LIMIT 100"""
        )

    def test_column_name_injection(self, mysql_schema):
        mysql_schema.columns[0].name = "column; DROP TABLE users;"
        query_builder = BaseQueryBuilder(mysql_schema)
        query = query_builder.build_query()
        assert (
            query
            == """SELECT
  "column; DROP TABLE users;",
  first_name,
  timestamp
FROM users
ORDER BY
  created_at DESC
LIMIT 100"""
        )

    def test_table_name_union_injection(self, mysql_schema):
        mysql_schema.name = "users UNION SELECT 1,2,3;"
        query_builder = BaseQueryBuilder(mysql_schema)
        query = query_builder.build_query()
        assert (
            query
            == """SELECT
  email,
  first_name,
  timestamp
FROM "users UNION SELECT 1,2,3;"
ORDER BY
  created_at DESC
LIMIT 100"""
        )

    def test_column_name_union_injection(self, mysql_schema):
        mysql_schema.columns[
            0
        ].name = "column UNION SELECT username, password FROM users;"
        query_builder = BaseQueryBuilder(mysql_schema)
        query = query_builder.build_query()
        assert (
            query
            == """SELECT
  "column UNION SELECT username, password FROM users;",
  first_name,
  timestamp
FROM users
ORDER BY
  created_at DESC
LIMIT 100"""
        )

    def test_table_name_comment_injection(self, mysql_schema):
        mysql_schema.name = "users --"
        query_builder = BaseQueryBuilder(mysql_schema)
        query = query_builder.build_query()
        assert (
            query
            == """SELECT
  email,
  first_name,
  timestamp
FROM users
ORDER BY
  created_at DESC
LIMIT 100"""
        )

    def test_column_name_comment_injection(self, mysql_schema):
        mysql_schema.columns[0].name = "column --"
        query_builder = BaseQueryBuilder(mysql_schema)
        query = query_builder.build_query()
        assert (
            query
            == """SELECT
  column,
  first_name,
  timestamp
FROM users
ORDER BY
  created_at DESC
LIMIT 100"""
        )

    def test_table_name_stacked_query_injection(self, mysql_schema):
        mysql_schema.name = 'users"; SELECT * FROM sensitive_data; --'
        query_builder = BaseQueryBuilder(mysql_schema)
        query = query_builder.build_query()
        assert (
            query
            == """SELECT
  email,
  first_name,
  timestamp
FROM "users""; SELECT * FROM sensitive_data; --"
ORDER BY
  created_at DESC
LIMIT 100"""
        )

    def test_table_name_batch_injection(self, mysql_schema):
        mysql_schema.name = "users; TRUNCATE users; SELECT * FROM users WHERE 't'='t"
        query_builder = BaseQueryBuilder(mysql_schema)
        query = query_builder.build_query()
        assert (
            query
            == """SELECT
  email,
  first_name,
  timestamp
FROM "users; TRUNCATE users; SELECT * FROM users WHERE 't'='t"
ORDER BY
  created_at DESC
LIMIT 100"""
        )

    def test_table_name_time_based_injection(self, mysql_schema):
        mysql_schema.name = "users' AND (SELECT * FROM (SELECT(SLEEP(5)))test); --"
        query_builder = BaseQueryBuilder(mysql_schema)
        query = query_builder.build_query()
        assert (
            query
            == """SELECT
  email,
  first_name,
  timestamp
FROM "users' AND (SELECT * FROM (SELECT(SLEEP(5)))test); --"
ORDER BY
  created_at DESC
LIMIT 100"""
        )

    @pytest.mark.parametrize(
        "injection",
        [
            "users; DROP TABLE users;",
            "users UNION SELECT 1,2,3;",
            'users"; SELECT * FROM sensitive_data; --',
            "users; TRUNCATE users; SELECT * FROM users WHERE 't'='t",
            "users' AND (SELECT * FROM (SELECT(SLEEP(5)))test); --",
        ],
    )
    def test_order_by_injection(self, injection, mysql_schema):
        mysql_schema.order_by = [injection]
        query_builder = BaseQueryBuilder(mysql_schema)
        with pytest.raises((sqlglot.errors.ParseError, sqlglot.errors.TokenError)):
            query_builder.build_query()
