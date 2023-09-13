import pandas as pd
from typing import Union

polars_imported = False
try:
    import polars as pl

    polars_imported = True
    DataFrameType = Union[pd.DataFrame, pl.DataFrame, str]
except ImportError:
    DataFrameType = Union[pd.DataFrame, str]


def df_type(df: DataFrameType) -> Union[str, None]:
    """
    Returns the type of the dataframe.

    Args:
        df (DataFrameType): Pandas or Polars dataframe

    Returns:
        str: Type of the dataframe
    """
    if polars_imported and isinstance(df, pl.DataFrame):
        return "polars"
    elif isinstance(df, pd.DataFrame):
        return "pandas"
    else:
        return None
