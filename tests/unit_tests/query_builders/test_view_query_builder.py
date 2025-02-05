import pytest

from pandasai.query_builders.view_query_builder import ViewQueryBuilder


class TestViewQueryBuilder:
    @pytest.fixture
    def view_query_builder(self, mysql_view_schema, mysql_view_dependencies_dict):
        return ViewQueryBuilder(mysql_view_schema, mysql_view_dependencies_dict)

    def test__init__(self, mysql_view_schema, mysql_view_dependencies_dict):
        query_builder = ViewQueryBuilder(
            mysql_view_schema, mysql_view_dependencies_dict
        )
        assert isinstance(query_builder, ViewQueryBuilder)
        assert query_builder.schema == mysql_view_schema

    def test_build_query(self, view_query_builder):
        assert (
            view_query_builder.build_query()
            == """SELECT
  parents_id,
  parents_name,
  children_name
FROM (
  SELECT
    parents.id AS parents_id,
    parents.name AS parents_name,
    children.name AS children_name
  FROM (
    SELECT
      *
    FROM parents
  ) AS parents
  JOIN (
    SELECT
      *
    FROM children
  ) AS children
    ON parents.id = children.id
) AS parent_children"""
        )

    def test_get_columns(self, view_query_builder):
        assert view_query_builder._get_columns() == [
            "parents_id",
            "parents_name",
            "children_name",
        ]

    def test_get_columns_empty(self, view_query_builder):
        view_query_builder.schema.columns = None
        assert view_query_builder._get_columns() == ["*"]

    def test_get_table_expression(self, view_query_builder):
        assert (
            view_query_builder._get_table_expression()
            == """(
  SELECT
    parents.id AS parents_id,
    parents.name AS parents_name,
    children.name AS children_name
  FROM (
    SELECT
      *
    FROM parents
  ) AS parents
  JOIN (
    SELECT
      *
    FROM children
  ) AS children
    ON parents.id = children.id
) AS parent_children"""
        )
