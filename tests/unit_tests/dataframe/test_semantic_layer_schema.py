import pytest
from pydantic import ValidationError

from pandasai.data_loader.semantic_layer_schema import (
    Destination,
    SemanticLayerSchema,
    Transformation,
    is_schema_source_same,
)


class TestSemanticLayerSchema:
    @pytest.fixture
    def sample_schema(self):
        return {
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
                "type": "csv",
                "path": "users.csv",
            },
        }

    @pytest.fixture
    def mysql_schema(self):
        return {
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

    @pytest.fixture
    def mysql_view_schema(self):
        return {
            "name": "parent-children",
            "columns": [
                {"name": "parents.id"},
                {"name": "parents.name"},
                {"name": "children.name"},
            ],
            "relations": [{"from": "parents.id", "to": "children.id"}],
            "view": "true",
        }

    def test_valid_schema(self, sample_schema):
        schema = SemanticLayerSchema(**sample_schema)

        assert schema.name == "Users"
        assert schema.update_frequency == "weekly"
        assert len(schema.columns) == 3
        assert schema.order_by == ["created_at DESC"]
        assert schema.limit == 100
        assert len(schema.transformations) == 2
        assert schema.source.type == "csv"

    def test_valid_mysql_schema(self, mysql_schema):
        schema = SemanticLayerSchema(**mysql_schema)

        assert schema.name == "Users"
        assert schema.update_frequency == "weekly"
        assert len(schema.columns) == 3
        assert schema.order_by == ["created_at DESC"]
        assert schema.limit == 100
        assert len(schema.transformations) == 2
        assert schema.source.type == "mysql"

    def test_valid_mysql_view_schema(self, mysql_view_schema):
        schema = SemanticLayerSchema(**mysql_view_schema)

        assert schema.name == "parent-children"
        assert len(schema.columns) == 3
        assert schema.view == True

    def test_missing_source_path(self, sample_schema):
        sample_schema["source"].pop("path")

        with pytest.raises(ValidationError):
            SemanticLayerSchema(**sample_schema)

    def test_missing_source_table(self, mysql_schema):
        mysql_schema["source"].pop("table")

        with pytest.raises(ValidationError):
            SemanticLayerSchema(**mysql_schema)

    def test_missing_mysql_connection(self, mysql_schema):
        mysql_schema["source"].pop("connection")

        with pytest.raises(ValidationError):
            SemanticLayerSchema(**mysql_schema)

    def test_invalid_schema_missing_name(self, sample_schema):
        sample_schema.pop("name")

        with pytest.raises(ValidationError):
            SemanticLayerSchema(**sample_schema)

    def test_invalid_column_type(self, sample_schema):
        sample_schema["columns"][0]["type"] = "unsupported"

        with pytest.raises(ValidationError):
            SemanticLayerSchema(**sample_schema)

    def test_invalid_source_type(self, sample_schema):
        sample_schema["source"]["type"] = "invalid"

        with pytest.raises(ValidationError):
            SemanticLayerSchema(**sample_schema)

    def test_valid_transformations(self):
        transformation_data = {
            "type": "anonymize",
            "params": {"column": "email"},
        }

        transformation = Transformation(**transformation_data)

        assert transformation.type == "anonymize"
        assert transformation.params["column"] == "email"

    def test_valid_destination(self):
        destination_data = {
            "type": "local",
            "format": "parquet",
            "path": "output.parquet",
        }

        destination = Destination(**destination_data)

        assert destination.type == "local"
        assert destination.format == "parquet"
        assert destination.path == "output.parquet"

    def test_invalid_destination_format(self):
        destination_data = {
            "type": "local",
            "format": "invalid",
            "path": "output.parquet",
        }

        with pytest.raises(ValidationError):
            Destination(**destination_data)

    def test_invalid_transformation_type(self):
        transformation_data = {
            "type": "unsupported_transformation",
            "params": {"column": "email"},
        }

        with pytest.raises(ValidationError):
            Transformation(**transformation_data)

    def test_is_schema_source_same_true(self, mysql_schema):
        schema1 = SemanticLayerSchema(**mysql_schema)
        schema2 = SemanticLayerSchema(**mysql_schema)

        assert is_schema_source_same(schema1, schema2) is True

    def test_is_schema_source_same_false(self, mysql_schema, sample_schema):
        schema1 = SemanticLayerSchema(**mysql_schema)
        schema2 = SemanticLayerSchema(**sample_schema)

        assert is_schema_source_same(schema1, schema2) is False

    def test_invalid_view_and_source(self, mysql_schema):
        mysql_schema["view"] = True

        with pytest.raises(ValidationError):
            SemanticLayerSchema(**mysql_schema)

    def test_invalid_source_missing_view_or_table(self, mysql_schema):
        mysql_schema["source"].pop("table")

        with pytest.raises(ValidationError):
            SemanticLayerSchema(**mysql_schema)

    def test_invalid_no_relation_for_view(self, mysql_view_schema):
        mysql_view_schema.pop("relations")

        with pytest.raises(ValidationError):
            SemanticLayerSchema(**mysql_view_schema)

    def test_invalid_duplicated_columns(self, sample_schema):
        sample_schema["columns"].append(sample_schema["columns"][0])

        with pytest.raises(ValidationError):
            SemanticLayerSchema(**sample_schema)

    def test_invalid_wrong_column_format_in_view(self, mysql_view_schema):
        mysql_view_schema["columns"][0]["name"] = "parentsid"

        with pytest.raises(ValidationError):
            SemanticLayerSchema(**mysql_view_schema)

    def test_invalid_wrong_column_format(self, sample_schema):
        sample_schema["columns"][0]["name"] = "parents.id"

        with pytest.raises(ValidationError):
            SemanticLayerSchema(**sample_schema)

    def test_invalid_wrong_relation_format_in_view(self, mysql_view_schema):
        mysql_view_schema["relations"][0]["to"] = "parentsid"

        with pytest.raises(ValidationError):
            SemanticLayerSchema(**mysql_view_schema)

    def test_invalid_uncovered_columns_in_view(self, mysql_view_schema):
        mysql_view_schema["relations"][0]["to"] = "parents.id"

        with pytest.raises(ValidationError):
            SemanticLayerSchema(**mysql_view_schema)
