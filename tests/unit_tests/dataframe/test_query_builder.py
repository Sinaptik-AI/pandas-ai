import pytest
from pandasai.data_loader.query_builder import QueryBuilder


class TestQueryBuilder:
    @pytest.fixture
    def sample_schema(self):
        return {
            "columns": [
                {"name": "email"},
                {"name": "first_name"},
                {"name": "timestamp"},
            ],
            "order_by": ["created_at DESC"],
            "limit": 100,
            "source": {
                "table": "users",
            },
        }

    def test_build_query(self, sample_schema):
        query_builder = QueryBuilder(sample_schema)
        query = query_builder.build_query()
        expected_query = "SELECT email, first_name, timestamp FROM users ORDER BY created_at DESC LIMIT 100"
        assert query == expected_query

    def test_build_query_without_order_by(self, sample_schema):
        schema_without_order_by = sample_schema.copy()
        del schema_without_order_by["order_by"]
        query_builder = QueryBuilder(schema_without_order_by)
        query = query_builder.build_query()
        expected_query = "SELECT email, first_name, timestamp FROM users LIMIT 100"
        assert query == expected_query

    def test_build_query_without_limit(self, sample_schema):
        schema_without_limit = sample_schema.copy()
        del schema_without_limit["limit"]
        query_builder = QueryBuilder(schema_without_limit)
        query = query_builder.build_query()
        expected_query = (
            "SELECT email, first_name, timestamp FROM users ORDER BY created_at DESC"
        )
        assert query == expected_query

    def test_build_query_with_multiple_order_by(self, sample_schema):
        schema_multiple_order_by = sample_schema.copy()
        schema_multiple_order_by["order_by"] = ["created_at DESC", "email ASC"]
        query_builder = QueryBuilder(schema_multiple_order_by)
        query = query_builder.build_query()
        expected_query = "SELECT email, first_name, timestamp FROM users ORDER BY created_at DESC, email ASC LIMIT 100"
        assert query == expected_query
