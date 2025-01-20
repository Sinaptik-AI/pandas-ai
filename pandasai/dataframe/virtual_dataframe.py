from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

import pandas as pd

from pandasai.data_loader.semantic_layer_schema import SemanticLayerSchema
from pandasai.dataframe.base import DataFrame
from pandasai.exceptions import VirtualizationError

if TYPE_CHECKING:
    from pandasai.data_loader.loader import DatasetLoader


class VirtualDataFrame(DataFrame):
    _metadata = [
        "_agent",
        "_column_hash",
        "_head",
        "_loader",
        "config",
        "description",
        "head",
        "name",
        "path",
        "schema",
    ]

    def __init__(self, *args, **kwargs):
        self._loader: DatasetLoader = kwargs.pop("data_loader", None)
        if not self._loader:
            raise VirtualizationError("Data loader is required for virtualization!")
        self._head = None

        schema: SemanticLayerSchema = kwargs.get("schema", None)
        if not schema:
            raise VirtualizationError("Schema is required for virtualization!")

        table_name = schema.source.table

        description = schema.description

        super().__init__(
            self.get_head(),
            name=table_name,
            description=description,
            *args,
            **kwargs,
        )

    def head(self):
        if self._head is None:
            self._head = self._loader.load_head()
        return self._head

    @property
    def rows_count(self) -> int:
        return self._loader.get_row_count()

    def execute_sql_query(self, query: str) -> pd.DataFrame:
        return self._loader.execute_query(query)
