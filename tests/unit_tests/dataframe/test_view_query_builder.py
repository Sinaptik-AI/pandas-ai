import pytest

from pandasai.data_loader.query_builder import QueryBuilder
from pandasai.data_loader.semantic_layer_schema import SemanticLayerSchema
from pandasai.data_loader.view_query_builder import ViewQueryBuilder


class TestViewQueryBuilder:
    @pytest.fixture
    def view_query_builder(self, mysql_view_schema, mysql_view_dependencies_dict):
        return ViewQueryBuilder(mysql_view_schema, mysql_view_dependencies_dict)

    def test__init__(self, mysql_view_schema, mysql_view_dependencies_dict):
        query_builder = ViewQueryBuilder(
            mysql_view_schema, mysql_view_dependencies_dict
        )
        assert isinstance(query_builder, ViewQueryBuilder)
        assert isinstance(query_builder, QueryBuilder)
        assert query_builder.schema == mysql_view_schema

    def test_format_query(self, view_query_builder):
        query = "SELECT * FROM table_llm_friendly"
        formatted_query = view_query_builder.format_query(query)
        assert formatted_query == "SELECT * FROM table_llm_friendly"

    def test_build_query(self, view_query_builder) -> str:
        assert (
            view_query_builder.build_query()
            == """SELECT parents_id, parents_name, children_name FROM ( SELECT
parents.id AS parents_id, parents.name AS parents_name, children.name AS children_name
FROM ( SELECT * FROM parents ) AS parents
JOIN ( SELECT * FROM children ) AS children
ON parents.id = children.id) AS parent-children
"""
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
        assert (
            view_query_builder._get_from_statement()
            == """FROM ( SELECT
parents.id AS parents_id, parents.name AS parents_name, children.name AS children_name
FROM ( SELECT * FROM parents ) AS parents
JOIN ( SELECT * FROM children ) AS children
ON parents.id = children.id) AS parent-children
"""
        )
