import pytest
import yaml
from pydantic import ValidationError
from pandasai.data_loader.semantic_layer_schema import (
    Destination,
    SemanticLayerSchema,
    Transformation,
    is_schema_source_same,
    Source,
    SQLConnectionConfig,
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

    def test_schema_to_dict_and_to_yaml(self, raw_sample_schema):
        """
        Test that the to_dict and to_yaml methods on SemanticLayerSchema produce the expected outputs.
        The test verifies that a valid schema can be converted to a dictionary (with proper keys)
        and then to a valid YAML formatted string containing the schema name.
        """
        schema = SemanticLayerSchema(**raw_sample_schema)
        schema_dict = schema.to_dict()
        assert isinstance(schema_dict, dict)
        assert "name" in schema_dict
        assert schema_dict["name"] == raw_sample_schema["name"]

        schema_yaml = schema.to_yaml()
        assert isinstance(schema_yaml, str)
        assert raw_sample_schema["name"] in schema_yaml

def test_invalid_rename_transformation_missing_new_name():
    """
    Test that a transformation of type "rename" without the required 'new_name' parameter
    raises a ValidationError.
    """
    transformation_data = {
        "type": "rename",
        "params": {"column": "first_name"}  # missing 'new_name'
    }
    with pytest.raises(ValidationError):
        Transformation(**transformation_data)

def test_source_is_compatible_source():
    """
    Test the is_compatible_source method to ensure:
    - Two local sources (e.g., CSV files) are compatible.
    - Two remote sources (e.g., MySQL) with identical connection configs are compatible.
    - Remote sources with different connection configs are not compatible.
    - A local source and a remote source are not compatible.
    """
    # Local sources: both should be compatible
    local_source_1 = Source(type="csv", path="file1.csv")
    local_source_2 = Source(type="csv", path="file2.csv")
    assert local_source_1.is_compatible_source(local_source_2) is True

    # Remote sources: create a common connection config
    connection = SQLConnectionConfig(
        host="localhost", port=3306, database="db", user="user", password="pass"
    )
    remote_source_1 = Source(type="mysql", connection=connection, table="table1")
    remote_source_2 = Source(type="mysql", connection=connection, table="table2")
    assert remote_source_1.is_compatible_source(remote_source_2) is True

    # Remote sources: using a different connection config should not be compatible
    connection2 = SQLConnectionConfig(
        host="localhost", port=3307, database="db2", user="user2", password="pass2"
    )
    remote_source_3 = Source(type="mysql", connection=connection2, table="table3")
    assert remote_source_1.is_compatible_source(remote_source_3) is False

    # Local vs Remote: should not be compatible
    assert local_source_1.is_compatible_source(remote_source_1) is False

def test_sql_connection_config_equality():
    """
    Test that SQLConnectionConfig.__eq__ correctly identifies equal and non-equal connection configurations.
    """
    conn1 = SQLConnectionConfig(host="localhost", port=3306, database="db", user="user", password="pass")
    conn2 = SQLConnectionConfig(host="localhost", port=3306, database="db", user="user", password="pass")
    conn3 = SQLConnectionConfig(host="localhost", port=3307, database="db", user="user", password="pass")
    assert conn1 == conn2, "Expected conn1 and conn2 to be considered equal."
    assert conn1 != conn3, "Expected conn1 and conn3 to be considered not equal."
import pytest
from pandasai.data_loader.semantic_layer_schema import SemanticLayerSchema


def test_valid_group_by_schema(self):
    """
    Test that a valid non-view schema with group_by defined correctly passes validation.
    Ensures that:
    - All non-aggregated columns (e.g., 'date') are included in group_by.
    - Aggregated columns (e.g., 'total' with expression 'sum') are not included in group_by.
    """
    schema_data = {
        "name": "Sales",
        "source": {"type": "csv", "path": "sales.csv"},
        "group_by": ["date"],
        "columns": [
            {"name": "date", "type": "string", "description": "Sales date"},
            {"name": "total", "type": "number", "description": "Total sales", "expression": "sum"}
        ],
    }
    schema = SemanticLayerSchema(**schema_data)
    assert schema.group_by == ["date"]
    # Verify that no errors are raised and the schema is valid.
    schema_dict = schema.to_dict()
    assert schema_dict["name"] == "Sales"
    assert "group_by" in schema_dict
import pytest
from pandasai.data_loader.semantic_layer_schema import SemanticLayerSchema


def test_valid_group_by_schema():
    """
    Test that a valid non-view schema with group_by defined correctly passes validation.
    Ensures that:
    - All non-aggregated columns (e.g., 'date') are included in group_by.
    - Aggregated columns (e.g., 'total' with expression 'sum') are not included in group_by.
    """
    schema_data = {
        "name": "Sales",
        "source": {"type": "csv", "path": "sales.csv"},
        "group_by": ["date"],
        "columns": [
            {"name": "date", "type": "string", "description": "Sales date"},
            {"name": "total", "type": "number", "description": "Total sales", "expression": "sum"}
        ],
    }
    schema = SemanticLayerSchema(**schema_data)
    assert schema.group_by == ["date"]
    # Verify that no errors are raised and the schema is valid.
    schema_dict = schema.to_dict()
    assert schema_dict["name"] == "Sales"
    assert "group_by" in schema_dict
import pytest
from pandasai.data_loader.semantic_layer_schema import SemanticLayerSchema


def test_valid_group_by_schema():
    """
    Test that a valid non-view schema with group_by defined correctly passes validation.
    Ensures that non-aggregated columns (e.g., 'date') are included in group_by and that
    aggregated columns (e.g., 'total' with expression 'sum') are allowed without being in group_by.
    """
    schema_data = {
        "name": "Sales",
        "source": {"type": "csv", "path": "sales.csv"},
        "group_by": ["date"],
        "columns": [
            {"name": "date", "type": "string", "description": "Sales date"},
            {"name": "total", "type": "number", "description": "Total sales", "expression": "sum"}
        ],
    }
    schema = SemanticLayerSchema(**schema_data)
    assert schema.group_by == ["date"]
    schema_dict = schema.to_dict()
    assert schema_dict["name"] == "Sales"
    assert "group_by" in schema_dict
