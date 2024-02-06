from pandasai.engine import _engine

if _engine == "modin":
    try:
        from modin.pandas import *

        __name__ = "modin.pandas"
    except ImportError as e:
        raise ImportError(
            "Could not import modin. Please install with `pip install modin[ray]`."
        ) from e
else:
    from pandas import *

    __name__ = "pandas"
