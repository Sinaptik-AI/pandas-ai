import datetime
import json

import numpy as np
import pandas as pd
import pytest

from pandasai.helpers.json_encoder import CustomJsonEncoder, convert_numpy_types


# Test cases for convert_numpy_types
@pytest.mark.parametrize(
    "input_value,expected_output",
    [
        ("string", None),
        (np.int32(42), 42),
        (np.float64(3.14), 3.14),
        (np.array([1, 2, 3]), [1, 2, 3]),
        ({"a": np.int8(7), "b": np.float32(2.5)}, {"a": 7, "b": 2.5}),
        ([np.uint16(10), np.float64(5.6)], [10, 5.6]),
    ],
)
def test_convert_numpy_types(input_value, expected_output):
    result = convert_numpy_types(input_value)
    assert result == expected_output


# Test cases for CustomJsonEncoder
def test_custom_json_encoder_numpy_types():
    # Arrange
    obj = {
        "integer": np.int32(123),
        "float": np.float64(1.23),
        "array": np.array([1, 2, 3]),
    }
    expected_json = '{"integer": 123, "float": 1.23, "array": [1, 2, 3]}'

    # Act
    result = json.dumps(obj, cls=CustomJsonEncoder)

    # Assert
    assert result == expected_json


def test_custom_json_encoder_pandas_types():
    # Arrange
    timestamp = pd.Timestamp("2025-01-01T12:00:00")
    dataframe = pd.DataFrame({"col1": [1, 2, 3]})
    obj = {
        "timestamp": timestamp,
        "dataframe": dataframe,
    }

    # Expected JSON
    expected_json = json.dumps(
        {
            "timestamp": "2025-01-01T12:00:00",
            "dataframe": {
                "index": [0, 1, 2],
                "columns": ["col1"],
                "data": [[1], [2], [3]],
            },
        }
    )

    # Act
    result = json.dumps(obj, cls=CustomJsonEncoder)

    # Assert
    assert result == expected_json


def test_custom_json_encoder_unsupported_type():
    # Arrange
    class UnsupportedType:
        pass

    obj = {"unsupported": UnsupportedType()}

    # Act & Assert
    with pytest.raises(TypeError):
        json.dumps(obj, cls=CustomJsonEncoder)


def test_custom_json_encoder_datetime():
    # Arrange
    dt = datetime.datetime(2025, 1, 1, 15, 30, 45)
    obj = {"datetime": dt}
    expected_json = '{"datetime": "2025-01-01T15:30:45"}'

    # Act
    result = json.dumps(obj, cls=CustomJsonEncoder)

    # Assert
    assert result == expected_json
