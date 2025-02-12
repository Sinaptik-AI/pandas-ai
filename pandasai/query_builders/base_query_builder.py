from typing import List

from sqlglot import select
from sqlglot.optimizer.normalize_identifiers import normalize_identifiers

from pandasai.data_loader.semantic_layer_schema import SemanticLayerSchema, Source


class BaseQueryBuilder:
    def __init__(self, schema: SemanticLayerSchema):
        self.schema = schema

    def build_query(self) -> str:
        query = select(*self._get_columns()).from_(self._get_table_expression())

        if self.schema.group_by:
            query = query.group_by(
                *[normalize_identifiers(col) for col in self.schema.group_by]
            )

        if self.schema.order_by:
            query = query.order_by(*self.schema.order_by)

        if self.schema.limit:
            query = query.limit(self.schema.limit)

        return query.sql(pretty=True)

    def get_head_query(self, n=5):
        # Start with base query
        query = select(*self._get_columns()).from_(self._get_table_expression())

        # Add GROUP BY if there are aggregations
        if self.schema.group_by:
            query = query.group_by(
                *[normalize_identifiers(col) for col in self.schema.group_by]
            )

        # Add LIMIT
        query = query.limit(n)

        return query.sql(pretty=True)

    def get_row_count(self):
        return select("COUNT(*)").from_(self._get_table_expression()).sql(pretty=True)

    def _get_columns(self) -> list[str]:
        if not self.schema.columns:
            return ["*"]

        columns = []
        for col in self.schema.columns:
            if col.expression:
                # Create a raw SQL expression for the function call
                column_name = normalize_identifiers(col.name).sql()
                column_expr = f"{col.expression}({column_name})"
            else:
                column_expr = normalize_identifiers(col.name).sql()

            if col.alias:
                column_expr = f"{column_expr} AS {col.alias}"

            columns.append(column_expr)

        return columns

    def _get_table_expression(self) -> str:
        return normalize_identifiers(self.schema.name).sql(pretty=True)

    @staticmethod
    def check_compatible_sources(sources: List[Source]) -> bool:
        base_source = sources[0]
        return all(base_source.is_compatible_source(source) for source in sources[1:])
