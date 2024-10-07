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


DataFrameType = Union[pd.DataFrame, str]

modin_imported = False

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
        df (DataFrameType): Pandas or Modin dataframe

    Returns:
        str: Type of the dataframe
    """
    if modin_imported and isinstance(df, mpd.DataFrame):
        return "modin"
    elif isinstance(df, pd.DataFrame):
        return "pandas"
    else:
        return None
