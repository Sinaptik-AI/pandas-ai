import os
import pytest
import pandas as pd
import duckdb

from pandasai.data_loader.local_loader import LocalDatasetLoader, DuckDBConnectionManager, ConfigManager
from pandasai.exceptions import MaliciousQueryError, InvalidDataSourceType
from pandasai.dataframe.base import DataFrame

# Dummy classes used to construct a minimal schema object for testing
class DummySource:
    def __init__(self, type, path):
        self.type = type
        self.path = path

class DummyColumn:
    def __init__(self, name, alias=None, expression=None):
        self.name = name
        self.alias = alias
        self.expression = expression

class DummySchema:
    def __init__(self, name, source, group_by=None, columns=None):
        self.name = name
        self.source = source
        self.group_by = group_by or []
        self.columns = columns or []

def test_execute_query_unsafe(monkeypatch):
    """
    Test execute_query to ensure that when an unsafe SQL query is provided,
    a MaliciousQueryError is raised. The test uses a valid dataset path format
    ("dummy-org/dummy-dataset") and mocks is_sql_query_safe to always return False,
    simulating an unsafe query.
    """
    # Force is_sql_query_safe to always return False to simulate an unsafe query.
    monkeypatch.setattr("pandasai.data_loader.local_loader.is_sql_query_safe", lambda query: False)
    
    dummy_source = DummySource("csv", "dummy.csv")
    schema = DummySchema("dummy_table", dummy_source)
    loader = LocalDatasetLoader(schema, "dummy-org/dummy-dataset")
    
    with pytest.raises(MaliciousQueryError):
        loader.execute_query("SELECT * FROM table;")

def test_execute_query_safe(monkeypatch):
    """
    Test execute_query to ensure that when a safe SQL query is provided,
    it returns the expected result. The test mocks is_sql_query_safe to always
    return True and monkeypatches DuckDBConnectionManager.sql to simulate a successful SQL execution.
    """
    monkeypatch.setattr("pandasai.data_loader.local_loader.is_sql_query_safe", lambda query: True)
    
    dummy_source = DummySource("csv", "dummy.csv")
    schema = DummySchema("dummy_table", dummy_source)
    loader = LocalDatasetLoader(schema, "dummy-org/dummy-dataset")
    
    # Create a dummy result that simulates the behavior of DuckDBConnectionManager.sql(query)
    class DummyResult:
        def df(self):
            return pd.DataFrame({"a": [1, 2, 3]})
    
    # Monkeypatch DuckDBConnectionManager.sql to always return an instance of DummyResult
    monkeypatch.setattr(DuckDBConnectionManager, "sql", lambda self, query: DummyResult())
    
    result_df = loader.execute_query("SELECT * FROM dummy_table;")
    expected_df = pd.DataFrame({"a": [1, 2, 3]})
    pd.testing.assert_frame_equal(result_df, expected_df)

def test_load_with_grouping(monkeypatch):
    """
    Test the load method of LocalDatasetLoader when a schema with group_by 
    and column expressions (aggregation) is provided.
    This test verifies that the DataFrame is grouped, aggregated by summing 'sales',
    and that the columns are filtered and renamed according to the schema.
    """
    # Create a dummy DataFrame that includes an extra "other" column that should be dropped.
    data = {
        "country": ["USA", "USA", "Canada"],
        "sales": [100, 200, 150],
        "other": [1, 2, 3]
    }
    test_df = pd.DataFrame(data)
    
    # Create a dummy schema with grouping on 'country'.
    # The 'sales' column is aggregated using sum and renamed to 'total_sales'.
    dummy_source = DummySource("csv", "dummy.csv")
    dummy_columns = [
        DummyColumn("country"),
        DummyColumn("sales", alias="total_sales", expression="sum")
    ]
    schema = DummySchema("dummy_table", dummy_source, group_by=["country"], columns=dummy_columns)
    
    loader = LocalDatasetLoader(schema, "dummy-org/dummy-dataset")
    # Monkeypatch _load_from_local_source to return our dummy DataFrame.
    monkeypatch.setattr(loader, "_load_from_local_source", lambda: test_df)
    # Monkeypatch _apply_transformations to be an identity function.
    monkeypatch.setattr(loader, "_apply_transformations", lambda df: df)
    
    # Execute the load method. It should apply grouping, aggregation, and column filtering/renaming.
    result = loader.load()
    # Extract the underlying pandas DataFrame.
    result_pd = getattr(result, "data", result)
    
    # The expected DataFrame after grouping should be:
    # - Grouped by 'country'
    # - 'sales' aggregated by sum (USA: 300, Canada: 150)
    # - Columns filtered and renamed (sales -> total_sales)
    expected_df = pd.DataFrame({
        "country": ["Canada", "USA"],
        "total_sales": [150, 300]
    })
    
    # Sort the DataFrames by 'country' to avoid ordering issues before asserting equality.
    pd.testing.assert_frame_equal(
        result_pd.sort_values(by="country").reset_index(drop=True),
        expected_df.sort_values(by="country").reset_index(drop=True)
    )

def test_read_csv_or_parquet_unsupported_format(monkeypatch):
    """
    Test that the _read_csv_or_parquet method raises a ValueError
    when an unsupported file format is provided.
    """
    # Create dummy file manager which returns the path unchanged.
    class DummyFileManager:
        def abs_path(self, path):
            return path
    
    # Create a dummy config that mimics what ConfigManager.get() should return.
    class DummyConfig:
        file_manager = DummyFileManager()
    
    # Monkeypatch ConfigManager.get to return our dummy config.
    monkeypatch.setattr("pandasai.data_loader.local_loader.ConfigManager.get", lambda: DummyConfig)
    
    # Create a dummy schema and LocalDatasetLoader instance.
    dummy_source = DummySource("csv", "dummy.csv")
    dummy_schema = DummySchema("dummy_table", dummy_source)
    loader = LocalDatasetLoader(dummy_schema, "dummy-org/dummy-dataset")
    
    # Calling _read_csv_or_parquet with an unsupported file format ('json') should raise ValueError.
    with pytest.raises(ValueError, match="Unsupported file format: json"):
        loader._read_csv_or_parquet("dummy_path", "json")
import os
import pytest
import pandas as pd
import duckdb

from pandasai.data_loader.local_loader import LocalDatasetLoader, DuckDBConnectionManager, ConfigManager
from pandasai.dataframe.base import DataFrame
from pandasai.exceptions import MaliciousQueryError, InvalidDataSourceType

# ... existing dummy classes (DummySource, DummyColumn, DummySchema) ...


def test_register_table(monkeypatch):
    """
    Test that register_table loads the dataset and registers the table.
    This function monkeypatches loader.load to return a dummy DataFrame and
    captures the call to DuckDBConnectionManager.register to ensure it is called
    with the correct schema name and DataFrame.
    """
    # Setup a dummy schema and LocalDatasetLoader instance.
    dummy_source = DummySource("csv", "dummy.csv")
    schema = DummySchema("registered_table", dummy_source)
    loader = LocalDatasetLoader(schema, "dummy-org/dummy-dataset")
    
    # Create a dummy pandas DataFrame and wrap it as a pandasai DataFrame.
    dummy_data = pd.DataFrame({"col": [1, 2, 3]})
    dummy_wrapper = DataFrame(dummy_data, schema=schema, path="dummy-org/dummy-dataset")
    
    # Monkeypatch the load method of loader to return our dummy wrapped DataFrame.
    monkeypatch.setattr(loader, "load", lambda: dummy_wrapper)
    
    # Prepare a container to capture parameters passed to register.
    register_call = {}

    def fake_register(self, table_name, df):
        register_call["table_name"] = table_name
        register_call["df"] = df

    # Monkeypatch DuckDBConnectionManager.register to our fake_register.
    monkeypatch.setattr(DuckDBConnectionManager, "register", fake_register)
    
    # Call register_table which should load the data and register it.
    loader.register_table()
    
    # Assert that the register method was called with the expected parameters.
    assert register_call.get("table_name") == "registered_table", "Expected table name not passed to register."
    assert register_call.get("df") == dummy_wrapper, "Expected DataFrame not passed to register."
import os
import pytest
import pandas as pd
import duckdb
from pandas.testing import assert_frame_equal

from pandasai.data_loader.local_loader import LocalDatasetLoader, DuckDBConnectionManager
from pandasai.dataframe.base import DataFrame
from pandasai.exceptions import MaliciousQueryError, InvalidDataSourceType

# ... existing dummy classes (DummySource, DummyColumn, DummySchema) ...


def test_register_table(monkeypatch):
    """
    Test that register_table loads the dataset and registers the table.
    This test monkeypatches loader.load to return a dummy wrapped DataFrame and
    replaces DuckDBConnectionManager.register to capture its call parameters.
    It then asserts that the table name passed is correct and compares the underlying
    pandas DataFrames using assert_frame_equal to avoid ambiguity errors.
    """
    # Set up a dummy schema and LocalDatasetLoader instance.
    dummy_source = DummySource("csv", "dummy.csv")
    schema = DummySchema("registered_table", dummy_source)
    loader = LocalDatasetLoader(schema, "dummy-org/dummy-dataset")
    
    # Create a dummy pandas DataFrame and wrap it as a pandasai DataFrame.
    dummy_data = pd.DataFrame({"col": [1, 2, 3]})
    dummy_wrapper = DataFrame(dummy_data, schema=schema, path="dummy-org/dummy-dataset")
    
    # Monkeypatch the load method of the loader to return our dummy wrapped DataFrame.
    monkeypatch.setattr(loader, "load", lambda: dummy_wrapper)
    
    # Prepare a container to capture parameters passed to DuckDBConnectionManager.register.
    register_call = {}
    
    def fake_register(self, table_name, df):
        register_call["table_name"] = table_name
        register_call["df"] = df

    # Monkeypatch DuckDBConnectionManager.register with fake_register.
    monkeypatch.setattr(DuckDBConnectionManager, "register", fake_register)
    
    # Execute register_table which should load the data and register it.
    loader.register_table()
    
    # Assert that the register method was called with the expected table name.
    assert register_call.get("table_name") == "registered_table", "Expected table name not passed to register."
    
    # Compare the underlying pandas DataFrames using assert_frame_equal instead of the '==' operator.
    assert_frame_equal(register_call.get("df").df, dummy_wrapper.df)
import os
import pytest
import pandas as pd
import duckdb
from pandas.testing import assert_frame_equal

from pandasai.data_loader.local_loader import LocalDatasetLoader, DuckDBConnectionManager
from pandasai.dataframe.base import DataFrame
from pandasai.exceptions import MaliciousQueryError, InvalidDataSourceType

# ... existing dummy classes
class DummySource:
    def __init__(self, type, path):
        self.type = type
        self.path = path

class DummyColumn:
    def __init__(self, name, alias=None, expression=None):
        self.name = name
        self.alias = alias
        self.expression = expression

class DummySchema:
    def __init__(self, name, source, columns=None, group_by=None):
        self.name = name
        self.source = source
        self.columns = columns if columns is not None else []
        self.group_by = group_by if group_by is not None else []


def test_register_table(monkeypatch):
    """
    Test that register_table loads the dataset and registers the table.
    This test monkeypatches the loader.load method to return a dummy wrapped DataFrame
    and replaces DuckDBConnectionManager.register to capture its call parameters.
    It then asserts that the table name passed is correct and compares the underlying
    pandas DataFrames using assert_frame_equal to avoid ambiguity errors.
    
    Note: This test accesses the underlying pandas DataFrame via the 'data' attribute.
    """
    # Set up a dummy schema with one column
    dummy_source = DummySource("csv", "dummy.csv")
    schema = DummySchema("registered_table", dummy_source, columns=[DummyColumn("col")])
    
    # Create a LocalDatasetLoader instance
    loader = LocalDatasetLoader(schema, "dummy-org/dummy-dataset")
    
    # Create a dummy pandas DataFrame and wrap it using the pandasai DataFrame wrapper.
    dummy_data = pd.DataFrame({"col": [1, 2, 3]})
    dummy_wrapper = DataFrame(dummy_data, schema=schema, path="dummy-org/dummy-dataset")
    
    # Monkeypatch the load method of the loader to return our dummy wrapped DataFrame.
    monkeypatch.setattr(loader, "load", lambda: dummy_wrapper)
    
    # Container to capture parameters passed to DuckDBConnectionManager.register.
    register_call = {}
    
    def fake_register(self, table_name, df):
        register_call["table_name"] = table_name
        register_call["df"] = df
    
    # Monkeypatch DuckDBConnectionManager.register with fake_register.
    monkeypatch.setattr(DuckDBConnectionManager, "register", fake_register)
    
    # Execute register_table to load the data and register it.
    loader.register_table()
    
    # Assert that the register method was called with the expected table name.
    assert register_call.get("table_name") == "registered_table", "Expected table name not passed to register."
    
    # Compare the underlying pandas DataFrames using the 'data' attribute.
    assert_frame_equal(register_call.get("df").data, dummy_wrapper.data)
