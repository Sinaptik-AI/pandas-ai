from unittest.mock import MagicMock

import pytest

from pandasai.data_loader.semantic_layer_schema import SemanticLayerSchema
from pandasai.data_loader.sql_loader import SQLDatasetLoader
from pandasai.query_builders.sql_query_builder import SqlQueryBuilder
from pandasai.query_builders.view_query_builder import ViewQueryBuilder


class TestViewQueryBuilder:
    @pytest.fixture
    def view_query_builder(self, mysql_view_schema, mysql_view_dependencies_dict):
        return ViewQueryBuilder(mysql_view_schema, mysql_view_dependencies_dict)

    def _create_mock_loader(self, table_name):
        """Helper method to create a mock loader for a table."""
        schema = SemanticLayerSchema(
            **{
                "name": table_name,
                "source": {
                    "type": "mysql",
                    "connection": {
                        "host": "localhost",
                        "port": 3306,
                        "database": "test_db",
                        "user": "test_user",
                        "password": "test_password",
                    },
                    "table": table_name,
                },
            }
        )
        mock_loader = MagicMock(spec=SQLDatasetLoader)
        mock_loader.schema = schema
        mock_loader.query_builder = SqlQueryBuilder(schema=schema)
        return mock_loader

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
  parents_id AS parents_id,
  parents_name AS parents_name,
  children_name AS children_name
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
            "parents_id AS parents_id",
            "parents_name AS parents_name",
            "children_name AS children_name",
        ]

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

    def test_table_name_injection(self, view_query_builder):
        view_query_builder.schema.name = "users; DROP TABLE users;"
        query = view_query_builder.build_query()
        assert (
            query
            == '''SELECT
  parents_id AS parents_id,
  parents_name AS parents_name,
  children_name AS children_name
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
) AS "users; DROP TABLE users;"'''
        )

    def test_column_name_injection(self, view_query_builder):
        view_query_builder.schema.columns[0].name = "column; DROP TABLE users;"
        query = view_query_builder.build_query()
        assert (
            query
            == """SELECT
  column__drop_table_users_ AS column__drop_table_users_,
  parents_name AS parents_name,
  children_name AS children_name
FROM (
  SELECT
    column__drop_table_users_ AS column__drop_table_users_,
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

    def test_table_name_union_injection(self, view_query_builder):
        view_query_builder.schema.name = "users UNION SELECT 1,2,3;"
        query = view_query_builder.build_query()
        assert (
            query
            == '''SELECT
  parents_id AS parents_id,
  parents_name AS parents_name,
  children_name AS children_name
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
) AS "users UNION SELECT 1,2,3;"'''
        )

    def test_column_name_union_injection(self, view_query_builder):
        view_query_builder.schema.columns[
            0
        ].name = "column UNION SELECT username, password FROM users;"
        query = view_query_builder.build_query()
        assert (
            query
            == """SELECT
  column_union_select_username__password_from_users_ AS column_union_select_username__password_from_users_,
  parents_name AS parents_name,
  children_name AS children_name
FROM (
  SELECT
    column_union_select_username__password_from_users_ AS column_union_select_username__password_from_users_,
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

    def test_table_name_comment_injection(self, view_query_builder):
        view_query_builder.schema.name = "users --"
        query = view_query_builder.build_query()
        assert (
            query
            == """SELECT
  parents_id AS parents_id,
  parents_name AS parents_name,
  children_name AS children_name
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
) AS users"""
        )

    def test_multiple_joins_same_table(self):
        """Test joining the same table multiple times with different conditions."""
        schema_dict = {
            "name": "health_combined",
            "columns": [
                {"name": "diabetes.age"},
                {"name": "diabetes.bloodpressure"},
                {"name": "heart.age"},
                {"name": "heart.restingbp"},
            ],
            "relations": [
                {"from": "diabetes.age", "to": "heart.age"},
                {"from": "diabetes.bloodpressure", "to": "heart.restingbp"},
            ],
            "view": "true",
        }
        schema = SemanticLayerSchema(**schema_dict)
        dependencies = {
            "diabetes": self._create_mock_loader("diabetes"),
            "heart": self._create_mock_loader("heart"),
        }
        query_builder = ViewQueryBuilder(schema, dependencies)

        assert (
            query_builder._get_table_expression()
            == """(
  SELECT
    diabetes.age AS diabetes_age,
    diabetes.bloodpressure AS diabetes_bloodpressure,
    heart.age AS heart_age,
    heart.restingbp AS heart_restingbp
  FROM (
    SELECT
      *
    FROM diabetes
  ) AS diabetes
  JOIN (
    SELECT
      *
    FROM heart
  ) AS heart
    ON diabetes.age = heart.age AND diabetes.bloodpressure = heart.restingbp
) AS health_combined"""
        )

    def test_three_table_join(self, mysql_view_dependencies_dict):
        """Test joining three different tables."""
        schema_dict = {
            "name": "patient_records",
            "columns": [
                {"name": "patients.id"},
                {"name": "diabetes.glucose"},
                {"name": "heart.cholesterol"},
            ],
            "relations": [
                {"from": "patients.id", "to": "diabetes.patient_id"},
                {"from": "patients.id", "to": "heart.patient_id"},
            ],
            "view": "true",
        }
        schema = SemanticLayerSchema(**schema_dict)
        dependencies = {
            "patients": self._create_mock_loader("patients"),
            "diabetes": self._create_mock_loader("diabetes"),
            "heart": self._create_mock_loader("heart"),
        }
        query_builder = ViewQueryBuilder(schema, dependencies)

        assert (
            query_builder._get_table_expression()
            == """(
  SELECT
    patients.id AS patients_id,
    diabetes.glucose AS diabetes_glucose,
    heart.cholesterol AS heart_cholesterol
  FROM (
    SELECT
      *
    FROM patients
  ) AS patients
  JOIN (
    SELECT
      *
    FROM diabetes
  ) AS diabetes
    ON patients.id = diabetes.patient_id
  JOIN (
    SELECT
      *
    FROM heart
  ) AS heart
    ON patients.id = heart.patient_id
) AS patient_records"""
        )

    def test_column_name_comment_injection(self, view_query_builder):
        view_query_builder.schema.columns[0].name = "column --"
        query = view_query_builder.build_query()
        assert (
            query
            == """SELECT
  column___ AS column___,
  parents_name AS parents_name,
  children_name AS children_name
FROM (
  SELECT
    column___ AS column___,
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
