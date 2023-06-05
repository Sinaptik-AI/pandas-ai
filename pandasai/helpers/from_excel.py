"""
Helper Module to Handle Data
This module collects the helper function on handling various Data Sources.

"""
from __future__ import annotations

import pandas as pd


def from_excel(file, sheet: str | int | None = 0) -> pd.DataFrame:
    """
    Return a pandas DataFrame from an Excel file.
    Wrapper for pandas.read_excel().

    Args:
        file (str):  A file path to be read
        sheet (str | int): Name of the sheet or Sheet No. Default is 0

    Returns (pd.DataFrame): A Pandas Dataframe

    """

    return pd.read_excel(file, sheet_name=sheet)
