import warnings

import pandas as pd
import pytest

from pandasai.config import Config
from pandasai.llm.fake import FakeLLM
from pandasai.smart_dataframe import SmartDataframe, load_smartdataframes


def test_smart_dataframe_init_basic():
    # Create a sample dataframe
    df = pd.DataFrame({"A": [1, 2, 3], "B": ["x", "y", "z"]})

    # Test initialization with minimal parameters
    with pytest.warns(DeprecationWarning):
        smart_df = SmartDataframe(df)

    assert smart_df._original_import is df
    assert isinstance(smart_df.dataframe, pd.DataFrame)
    assert smart_df._table_name is None
    assert smart_df._table_description is None
    assert smart_df._custom_head is None


def test_smart_dataframe_init_with_all_params():
    # Create sample dataframes
    df = pd.DataFrame({"A": [1, 2, 3], "B": ["x", "y", "z"]})
    custom_head = pd.DataFrame({"A": [1], "B": ["x"]})
    config = Config(llm=FakeLLM())

    # Test initialization with all parameters
    with pytest.warns(DeprecationWarning):
        smart_df = SmartDataframe(
            df,
            name="test_df",
            description="Test dataframe",
            custom_head=custom_head,
            config=config,
        )

    assert smart_df._original_import is df
    assert isinstance(smart_df.dataframe, pd.DataFrame)
    assert smart_df._table_name == "test_df"
    assert smart_df._table_description == "Test dataframe"
    assert smart_df._custom_head == custom_head.to_csv(index=False)
    assert smart_df._agent._state._config == config


def test_smart_dataframe_deprecation_warning():
    df = pd.DataFrame({"A": [1, 2, 3]})

    with warnings.catch_warnings(record=True) as warning_info:
        warnings.simplefilter("always")
        SmartDataframe(df)

        deprecation_warnings = [
            w for w in warning_info if issubclass(w.category, DeprecationWarning)
        ]
        assert len(deprecation_warnings) >= 1
        assert "SmartDataframe will soon be deprecated" in str(
            deprecation_warnings[0].message
        )


def test_load_df_success():
    # Create sample dataframes
    original_df = pd.DataFrame({"A": [1, 2, 3], "B": ["x", "y", "z"]})
    with pytest.warns(DeprecationWarning):
        smart_df = SmartDataframe(original_df)

    # Test loading a new dataframe
    new_df = pd.DataFrame({"C": [4, 5, 6], "D": ["a", "b", "c"]})
    loaded_df = smart_df.load_df(
        new_df,
        name="new_df",
        description="New test dataframe",
        custom_head=pd.DataFrame({"C": [4], "D": ["a"]}),
    )

    assert isinstance(loaded_df, pd.DataFrame)
    assert loaded_df.equals(new_df)


def test_load_df_invalid_input():
    # Create a sample dataframe
    original_df = pd.DataFrame({"A": [1, 2, 3], "B": ["x", "y", "z"]})
    with pytest.warns(DeprecationWarning):
        smart_df = SmartDataframe(original_df)

    # Test loading invalid data
    with pytest.raises(
        ValueError, match="Invalid input data. We cannot convert it to a dataframe."
    ):
        smart_df.load_df(
            "not a dataframe",
            name="invalid_df",
            description="Invalid test data",
            custom_head=None,
        )


def test_load_smartdataframes():
    # Create sample dataframes
    df1 = pd.DataFrame({"A": [1, 2, 3], "B": ["x", "y", "z"]})
    df2 = pd.DataFrame({"C": [4, 5, 6], "D": ["a", "b", "c"]})

    # Create a config with FakeLLM
    config = Config(llm=FakeLLM())

    # Test loading regular pandas DataFrames
    smart_dfs = load_smartdataframes([df1, df2], config)
    assert len(smart_dfs) == 2
    assert all(isinstance(df, SmartDataframe) for df in smart_dfs)
    assert all(hasattr(df, "config") for df in smart_dfs)

    # Test loading mixed pandas DataFrames and SmartDataframes
    existing_smart_df = SmartDataframe(df1, config=config)
    mixed_dfs = load_smartdataframes([existing_smart_df, df2], config)
    assert len(mixed_dfs) == 2
    assert mixed_dfs[0] is existing_smart_df  # Should return the same instance
    assert isinstance(mixed_dfs[1], SmartDataframe)
    assert hasattr(mixed_dfs[1], "config")
