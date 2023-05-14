"""
This module contains helper functions for pulling data from different sources, Ex. Google Sheets, Excel, etc..
"""


import pandas as pd


def sheets_input(sheet_id, sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    return pd.read_csv(url)
