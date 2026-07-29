from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import pandas as pd

from pandasai.dataframe.base import DataFrame
from pandasai.exceptions import VirtualizationError

if TYPE_CHECKING:
    from pandasai.data_loader.sql_loader import SQLDatasetLoader


class VirtualDataFrame(DataFrame):
    _metadata = [
        "_agent",
        "_column_hash",
        "_head",
        "_loader",
        "_rows_count",
        "config",
        "head",
        "path",
        "schema",
    ]

    def __init__(self, *args, **kwargs):
        self._loader: Optional[SQLDatasetLoader] = kwargs.pop("data_loader", None)
        if not self._loader:
            raise VirtualizationError("Data loader is required for virtualization!")
        self._head = None
        self._rows_count = None

        super().__init__(
            *args,
            **kwargs,
        )

    def head(self):
        if self._head is None:
            self._head = self._loader.load_head()
        return self._head

    @property
    def rows_count(self) -> int:
        if self._rows_count is None:
            self._rows_count = self._loader.get_row_count()
        return self._rows_count

    @property
    def columns_count(self) -> int:
        # The backing pandas frame holds no data, so len(self.columns) is always 0
        # here. The schema is authoritative when it declares columns; otherwise fall
        # back to the head, which is cached.
        if self.schema.columns:
            return len(self.schema.columns)
        return len(self.head().columns)

    @property
    def query_builder(self):
        return self._loader.query_builder

    def execute_sql_query(self, query: str) -> pd.DataFrame:
        return self._loader.execute_query(query)
