import pandas as pd

from .base_restricted_module import BaseRestrictedModule


class RestrictedPandas(BaseRestrictedModule):
    def __init__(self):
        self.allowed_attributes = [
            # DataFrame creation and basic operations
            "DataFrame",
            "Series",
            "concat",
            "merge",
            "join",
            # Data manipulation
            "groupby",
            "pivot",
            "pivot_table",
            "melt",
            "crosstab",
            "cut",
            "qcut",
            "get_dummies",
            "factorize",
            # Indexing and selection
            "loc",
            "iloc",
            "at",
            "iat",
            # Function application
            "apply",
            "applymap",
            "pipe",
            # Reshaping and sorting
            "sort_values",
            "sort_index",
            "nlargest",
            "nsmallest",
            "rank",
            "reindex",
            "reset_index",
            "set_index",
            # Computations / descriptive stats
            "sum",
            "prod",
            "min",
            "max",
            "mean",
            "median",
            "var",
            "std",
            "sem",
            "skew",
            "kurt",
            "quantile",
            "count",
            "nunique",
            "value_counts",
            "describe",
            "cov",
            "corr",
            # Date functionality
            "to_datetime",
            "date_range",
            # String methods
            "str",
            # Categorical methods
            "Categorical",
            "cut",
            "qcut",
            # Plotting (if visualization is allowed)
            "plot",
            # Utility functions
            "isnull",
            "notnull",
            "isna",
            "notna",
            "fillna",
            "dropna",
            "replace",
            "astype",
            "copy",
            "drop_duplicates",
            # Window functions
            "rolling",
            "expanding",
            "ewm",
            # Time series functionality
            "resample",
            "shift",
            "diff",
            "pct_change",
            # Aggregation
            "agg",
            "aggregate",
        ]

        for attr in self.allowed_attributes:
            if hasattr(pd, attr):
                setattr(self, attr, self._wrap_function(getattr(pd, attr)))
            elif attr in ["loc", "iloc", "at", "iat"]:
                # These are properties, not functions
                setattr(
                    self, attr, property(lambda self, a=attr: getattr(pd.DataFrame, a))
                )

    def __getattr__(self, name):
        if name not in self.allowed_attributes:
            raise AttributeError(f"'{name}' is not allowed in RestrictedPandas")
        return getattr(pd, name)
