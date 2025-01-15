import pytest

from pandasai.data_loader.query_builder import QueryBuilder
from pandasai.data_loader.semantic_layer_schema import SemanticLayerSchema


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
            "destination": {
                "type": "local",
                "format": "parquet",
                "path": "users.parquet",
            },
        }
        return SemanticLayerSchema(**raw_schema)

    def test_build_query(self, mysql_schema):
        query_builder = QueryBuilder(mysql_schema)
        query = query_builder.build_query()
        expected_query = "SELECT email, first_name, timestamp FROM users ORDER BY created_at DESC LIMIT 100"
        assert query == expected_query

    def test_build_query_without_order_by(self, mysql_schema):
        mysql_schema.order_by = None
        query_builder = QueryBuilder(mysql_schema)
        query = query_builder.build_query()
        expected_query = "SELECT email, first_name, timestamp FROM users LIMIT 100"
        assert query == expected_query

    def test_build_query_without_limit(self, mysql_schema):
        mysql_schema.limit = None
        query_builder = QueryBuilder(mysql_schema)
        query = query_builder.build_query()
        expected_query = (
            "SELECT email, first_name, timestamp FROM users ORDER BY created_at DESC"
        )
        assert query == expected_query

    def test_build_query_with_multiple_order_by(self, mysql_schema):
        mysql_schema.order_by = ["created_at DESC", "email ASC"]
        query_builder = QueryBuilder(mysql_schema)
        query = query_builder.build_query()
        expected_query = "SELECT email, first_name, timestamp FROM users ORDER BY created_at DESC, email ASC LIMIT 100"
        assert query == expected_query
