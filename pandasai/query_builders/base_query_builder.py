import re
from typing import Any, List

import sqlglot
from sqlglot import from_, pretty, select
from sqlglot.expressions import Limit, cast

from pandasai.data_loader.semantic_layer_schema import SemanticLayerSchema, Source


class BaseQueryBuilder:
    def __init__(self, schema: SemanticLayerSchema):
        self.schema = schema

    def build_query(self) -> str:
        query = select(*self._get_columns()).from_(self._get_table_expression())

        if self.schema.limit:
            query = query.limit(self.schema.limit)

        if self.schema.order_by:
            query = query.order_by(*self.schema.order_by)

        return query.sql(pretty=True)

    def get_head_query(self, n=5):
        query = (
            select(*self._get_columns()).from_(self._get_table_expression()).limit(n)
        )
        return query.sql(pretty=True)

    def get_row_count(self):
        return select("COUNT(*)").from_(self._get_table_expression()).sql(pretty=True)

    def _get_columns(self) -> list[str]:
        if self.schema.columns:
            return [col.name for col in self.schema.columns]
        else:
            return ["*"]

    def _get_table_expression(self) -> str:
        return self.schema.name

    @staticmethod
    def check_compatible_sources(sources: List[Source]) -> bool:
        base_source = sources[0]
        return all(base_source.is_compatible_source(source) for source in sources[1:])
