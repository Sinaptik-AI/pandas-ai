"""Regression test: a NaN/inf numeric result must be rejected, not returned as valid.

NaN and inf are floats, so they pass the isinstance(value, (int, float, np.int64))
check in _validate_response and would be wrapped in a NumberResponse and returned as
the answer. They almost always come from an aggregation over an empty result
(e.g. df["sales"].mean() when a WHERE clause matched zero rows).

  with the fix -> PASS (raises InvalidOutputValueMismatch)
  without it   -> FAIL (returns NumberResponse(nan) silently)
"""
import numpy as np
import pytest

from pandasai.core.response.parser import ResponseParser
from pandasai.exceptions import InvalidOutputValueMismatch


def test_nan_number_rejected():
    parser = ResponseParser()
    with pytest.raises(InvalidOutputValueMismatch, match="NaN"):
        parser.parse({"type": "number", "value": float("nan")})


def test_inf_number_rejected():
    parser = ResponseParser()
    with pytest.raises(InvalidOutputValueMismatch, match="NaN"):
        parser.parse({"type": "number", "value": float("inf")})


def test_normal_number_still_ok():
    parser = ResponseParser()
    resp = parser.parse({"type": "number", "value": 42})
    assert resp.value == 42
