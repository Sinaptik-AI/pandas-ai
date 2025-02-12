import pytest
from pydantic import ValidationError
import yaml
from pandasai.data_loader.semantic_layer_schema import (
    Source,
    SQLConnectionConfig,
    Destination,
    SemanticLayerSchema,
    Transformation,
    is_schema_source_same,
)

class TestSemanticLayerSchema:
    def test_valid_schema(self, raw_sample_schema):
        schema = SemanticLayerSchema(**raw_sample_schema)
        assert schema.name == "Users"
        assert schema.update_frequency == "weekly"
        assert len(schema.columns) == 3
        assert schema.order_by == ["created_at DESC"]
        assert schema.limit == 100
        assert len(schema.transformations) == 2
        assert schema.source.type == "csv"

    def test_valid_raw_mysql_schema(self, raw_mysql_schema):
        schema = SemanticLayerSchema(**raw_mysql_schema)
        assert schema.name == "users"
        assert schema.update_frequency == "weekly"
        assert len(schema.columns) == 3
        assert schema.order_by == ["created_at DESC"]
        assert schema.limit == 100
        assert len(schema.transformations) == 2
        assert schema.source.type == "mysql"

    def test_valid_raw_mysql_view_schema(self, raw_mysql_view_schema):
        schema = SemanticLayerSchema(**raw_mysql_view_schema)
        assert schema.name == "parent_children"
        assert len(schema.columns) == 3
        assert schema.view is True

    def test_missing_source_path(self, raw_sample_schema):
        raw_sample_schema["source"].pop("path")
        with pytest.raises(ValidationError):
            SemanticLayerSchema(**raw_sample_schema)

    def test_missing_source_table(self, raw_mysql_schema):
        raw_mysql_schema["source"].pop("table")
        with pytest.raises(ValidationError):
            SemanticLayerSchema(**raw_mysql_schema)

    def test_missing_mysql_connection(self, raw_mysql_schema):
        raw_mysql_schema["source"].pop("connection")
        with pytest.raises(ValidationError):
            SemanticLayerSchema(**raw_mysql_schema)

    def test_invalid_schema_missing_name(self, raw_sample_schema):
        raw_sample_schema.pop("name")
        with pytest.raises(ValidationError):
            SemanticLayerSchema(**raw_sample_schema)

    def test_invalid_column_type(self, raw_sample_schema):
        raw_sample_schema["columns"][0]["type"] = "unsupported"
        with pytest.raises(ValidationError):
            SemanticLayerSchema(**raw_sample_schema)

    def test_invalid_source_type(self, raw_sample_schema):
        raw_sample_schema["source"]["type"] = "invalid"
        with pytest.raises(ValidationError):
            SemanticLayerSchema(**raw_sample_schema)

    def test_valid_transformations(self):
        transformation_data = {
            "type": "anonymize",
            "params": {"column": "email"},
        }
        transformation = Transformation(**transformation_data)
        assert transformation.type == "anonymize"
        assert transformation.params.column == "email"

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

    def test_is_schema_source_same_true(self, raw_mysql_schema):
        schema1 = SemanticLayerSchema(**raw_mysql_schema)
        schema2 = SemanticLayerSchema(**raw_mysql_schema)
        assert is_schema_source_same(schema1, schema2) is True

    def test_is_schema_source_same_false(self, raw_mysql_schema, raw_sample_schema):
        schema1 = SemanticLayerSchema(**raw_mysql_schema)
        schema2 = SemanticLayerSchema(**raw_sample_schema)
        assert is_schema_source_same(schema1, schema2) is False

    def test_invalid_view_and_source(self, raw_mysql_schema):
        raw_mysql_schema["view"] = True
        with pytest.raises(ValidationError):
            SemanticLayerSchema(**raw_mysql_schema)

    def test_invalid_source_missing_view_or_table(self, raw_mysql_schema):
        raw_mysql_schema["source"].pop("table")
        with pytest.raises(ValidationError):
            SemanticLayerSchema(**raw_mysql_schema)

    def test_invalid_no_relation_for_view(self, raw_mysql_view_schema):
        raw_mysql_view_schema.pop("relations")
        with pytest.raises(ValidationError):
            SemanticLayerSchema(**raw_mysql_view_schema)

    def test_invalid_duplicated_columns(self, raw_sample_schema):
        raw_sample_schema["columns"].append(raw_sample_schema["columns"][0])
        with pytest.raises(ValidationError):
            SemanticLayerSchema(**raw_sample_schema)

    def test_invalid_wrong_column_format_in_view(self, raw_mysql_view_schema):
        raw_mysql_view_schema["columns"][0]["name"] = "parentsid"
        with pytest.raises(ValidationError):
            SemanticLayerSchema(**raw_mysql_view_schema)

    def test_invalid_wrong_column_format(self, raw_sample_schema):
        raw_sample_schema["columns"][0]["name"] = "parents.id"
        with pytest.raises(ValidationError):
            SemanticLayerSchema(**raw_sample_schema)

    def test_invalid_wrong_relation_format_in_view(self, raw_mysql_view_schema):
        raw_mysql_view_schema["relations"][0]["to"] = "parentsid"
        with pytest.raises(ValidationError):
            SemanticLayerSchema(**raw_mysql_view_schema)

    def test_invalid_uncovered_columns_in_view(self, raw_mysql_view_schema):
        raw_mysql_view_schema["relations"][0]["to"] = "parents.id"
        with pytest.raises(ValidationError):
            SemanticLayerSchema(**raw_mysql_view_schema)

    def test_invalid_rename_transformation_missing_new_name(self):
        """
        Test that a 'rename' transformation fails validation if the required 'new_name' parameter is missing.
        """
        transformation_data = {"type": "rename", "params": {"column": "username"}}
        with pytest.raises(ValidationError):
            Transformation(**transformation_data)

    def test_to_yaml_conversion(self, raw_sample_schema):
        """
        Test that converting a SemanticLayerSchema instance to YAML produces a valid YAML string.
        The YAML string should correctly represent the schema's dictionary and be loadable back
        to a dictionary that is equal to the schema's dict representation.
        """
        schema = SemanticLayerSchema(**raw_sample_schema)
        yaml_str = schema.to_yaml()
        assert isinstance(yaml_str, str)
        loaded_dict = yaml.safe_load(yaml_str)
        assert loaded_dict == schema.to_dict()


def test_to_yaml_conversion(raw_sample_schema):
    """
    Test that converting a SemanticLayerSchema instance to YAML produces a valid YAML string.
    The YAML string is loadable back into a dictionary that matches the schema's dict representation.
    """
    schema = SemanticLayerSchema(**raw_sample_schema)
    yaml_str = schema.to_yaml()
    assert isinstance(yaml_str, str)
    loaded_dict = yaml.safe_load(yaml_str)
    assert loaded_dict == schema.to_dict()


def test_source_compatibility():
    """
    Test the compatibility checks of Source objects for both local and remote sources.
    It verifies that:
      - Two local sources are compatible.
      - Two remote sources with the same connection are compatible.
      - Two remote sources with different connections are not compatible.
      - A local source and a remote source are not compatible.
    """
    # Test local sources compatibility: both are local sources.
    local_source1 = Source(type="csv", path="data1.csv")
    local_source2 = Source(type="csv", path="data2.csv")
    assert local_source1.is_compatible_source(local_source2) is True

    # Test remote sources compatibility: both have identical connections.
    connection = SQLConnectionConfig(
        host="127.0.0.1", port=5432, database="testdb", user="admin", password="secret"
    )
    remote_source1 = Source(type="mysql", connection=connection, table="users")
    remote_source2 = Source(type="mysql", connection=connection, table="orders")
    assert remote_source1.is_compatible_source(remote_source2) is True

    # Test remote sources incompatibility: differing connection details.
    connection_diff = SQLConnectionConfig(
        host="127.0.0.1", port=5432, database="testdb", user="admin", password="different_secret"
    )
    remote_source3 = Source(type="mysql", connection=connection_diff, table="users")
    assert remote_source1.is_compatible_source(remote_source3) is False

    # Test that a local source and a remote source are not compatible.
    assert local_source1.is_compatible_source(remote_source1) is False
