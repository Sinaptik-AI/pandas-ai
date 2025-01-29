import pytest

from pandasai.data_loader.query_builder import QueryBuilder
from pandasai.data_loader.semantic_layer_schema import SemanticLayerSchema
from pandasai.data_loader.view_query_builder import ViewQueryBuilder


class TestViewQueryBuilder:
    @pytest.fixture
    def mysql_view_schema(self):
        raw_schema = {
            "name": "Users",
            "columns": [
                {"name": "parents.id"},
                {"name": "parents.name"},
                {"name": "children.name"},
            ],
            "relations": [{"from": "parents.id", "to": "children.id"}],
            "view": "true",
        }
        return SemanticLayerSchema(**raw_schema)

    @pytest.fixture
    def view_query_builder(self, mysql_view_schema):
        return ViewQueryBuilder(mysql_view_schema)

    def test__init__(self, mysql_view_schema):
        query_builder = ViewQueryBuilder(mysql_view_schema)
        assert isinstance(query_builder, ViewQueryBuilder)
        assert isinstance(query_builder, QueryBuilder)
        assert query_builder.schema == mysql_view_schema

    def test_format_query(self, view_query_builder):
        query = "SELECT ALL"
        formatted_query = view_query_builder.format_query(query)
        assert (
            formatted_query
            == """WITH Users AS ( SELECT
parents.id AS parents_id, parents.name AS parents_name, children.name AS children_name
FROM parents
JOIN children ON parents.id = children.id)
SELECT ALL"""
        )

    def test_build_query(self, view_query_builder) -> str:
        assert (
            view_query_builder.build_query()
            == """WITH Users AS ( SELECT
parents.id AS parents_id, parents.name AS parents_name, children.name AS children_name
FROM parents
JOIN children ON parents.id = children.id)
SELECT parents_id, parents_name, children_name FROM Users"""
        )

    def test_get_columns(self, view_query_builder):
        assert (
            view_query_builder._get_columns()
            == """parents_id, parents_name, children_name"""
        )

    def test_get_columns_empty(self, view_query_builder):
        view_query_builder.schema.columns = None
        assert view_query_builder._get_columns() == "*"

    def test_get_from_statement(self, view_query_builder):
        assert view_query_builder._get_from_statement() == " FROM Users"

    def test_get_with_statement(self, view_query_builder):
        assert (
            view_query_builder._get_with_statement()
            == """WITH Users AS ( SELECT
parents.id AS parents_id, parents.name AS parents_name, children.name AS children_name
FROM parents
JOIN children ON parents.id = children.id)
"""
        )

    def test_get_with_statement_no_columns(self, view_query_builder):
        view_query_builder.schema.columns = None
        assert (
            view_query_builder._get_with_statement()
            == """WITH Users AS ( SELECT
*
FROM parents
JOIN children ON parents.id = children.id)
"""
        )
