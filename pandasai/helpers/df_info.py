from typing import Union

import pandas as pd


def _import_modin():
    try:
        import modin.pandas as pd
    except ImportError as e:
        raise ImportError(
            "Could not import modin, please install with " "`pip install modin`."
        ) from e
    return pd


def _import_polars():
    try:
        import polars as pl
    except ImportError as e:
        raise ImportError(
            "Could not import polars, please install with " "`pip install polars`."
        ) from e
    return pl


DataFrameType = Union[pd.DataFrame, str]

polars_imported = False
modin_imported = False
try:
    pl = _import_polars()

    polars_imported = True
    DataFrameType = Union[DataFrameType, pl.DataFrame]
except ImportError:
    pass

try:
    mpd = _import_modin()

    modin_imported = True
    DataFrameType = Union[DataFrameType, mpd.DataFrame]
except ImportError:
    pass


def df_type(df: DataFrameType) -> Union[str, None]:
    """
    Returns the type of the dataframe.

    Args:
        df (DataFrameType): Pandas, Modin or Polars dataframe

    Returns:
        str: Type of the dataframe
    """
    if polars_imported and isinstance(df, pl.DataFrame):
        return "polars"
    elif modin_imported and isinstance(df, mpd.DataFrame):
        return "modin"
    elif isinstance(df, pd.DataFrame):
        return "pandas"
    else:
        return None
