"""Functions to return a dataframe from an Excel file."""
from __future__ import annotations

import pandas as pd


def from_excel(file, sheet: str | int | None = 0) -> pd.DataFrame:
    """
    Return a pandas DataFrame from an Excel file.
    Wrapper for pandas.read_excel().

    :param file: str, Path to the Excel file to read from.
    :param sheet: str, int, None, default = 0 Name of the sheet to read in,
        or the sheet number (0-indexed). Defaults to the first sheet.
    :return: pd.DataFrame, Dataframe containing the data from the specified sheet.
    """
    return pd.read_excel(file, sheet_name=sheet)
