import pandas as pd
import pytest

from pandasai.core.response.dataframe import DataFrameResponse


@pytest.fixture
def sample_dict_data():
    return {"col1": [1, 2, 3], "col2": ["a", "b", "c"]}


@pytest.fixture
def sample_df(sample_dict_data):
    return pd.DataFrame(sample_dict_data)


def test_dataframe_response_initialization(sample_df):
    response = DataFrameResponse(sample_df, "test_code")
    assert response.type == "dataframe"
    assert isinstance(response.value, pd.DataFrame)
    assert response.last_code_executed == "test_code"
    pd.testing.assert_frame_equal(response.value, sample_df)


def test_dataframe_response_minimal():
    empty_df = pd.DataFrame()
    response = DataFrameResponse(empty_df)
    assert response.type == "dataframe"
    assert isinstance(response.value, pd.DataFrame)
    assert response.last_code_executed is None
    assert response.value.empty


def test_dataframe_response_with_dict(sample_dict_data):
    response = DataFrameResponse(sample_dict_data, "test_code")
    assert response.type == "dataframe"
    assert isinstance(response.value, pd.DataFrame)
    assert list(response.value.columns) == ["col1", "col2"]
    assert len(response.value) == 3


def test_dataframe_response_with_existing_dataframe(sample_df):
    response = DataFrameResponse(sample_df, "test_code")
    assert response.type == "dataframe"
    assert isinstance(response.value, pd.DataFrame)
    pd.testing.assert_frame_equal(response.value, sample_df)


def test_format_value_with_dict(sample_dict_data):
    response = DataFrameResponse(pd.DataFrame())  # Initialize with empty DataFrame
    result = response.format_value(sample_dict_data)
    assert isinstance(result, pd.DataFrame)
    assert list(result.columns) == ["col1", "col2"]


def test_format_value_with_dataframe(sample_df):
    response = DataFrameResponse(pd.DataFrame())  # Initialize with empty DataFrame
    result = response.format_value(sample_df)
    assert isinstance(result, pd.DataFrame)
    pd.testing.assert_frame_equal(result, sample_df)
