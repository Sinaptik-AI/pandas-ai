import pandas as pd
from pandas.testing import assert_frame_equal

from pandasai.helpers import from_google_sheets


def test_from_google_sheets():
    # this is a public spreadsheet created for testing purposes
    url = (
        "https://docs.google.com/spreadsheets/d/"
        "1TRG676CAoHz3hPur3myBLlR0dl31qwc2xw8MzBlrEJw/edit?usp=sharing"
    )

    expected_output = [
        pd.DataFrame(
            {"A": [1, 2, 3], "B": ["foo", "bar", "baz"], "C": [1.0, 2.0, 3.0]}
        ),
        pd.DataFrame(
            {"X": [4, 5, 6], "Y": ["qux", "quux", "corge"], "Z": [4.0, 5.0, 6.0]}
        ),
    ]
    actual_output = from_google_sheets(url)
    for i in range(len(expected_output)):
        assert_frame_equal(actual_output[i], expected_output[i])
