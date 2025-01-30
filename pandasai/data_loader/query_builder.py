from typing import Any, Dict, List, Union

from pandasai.data_loader.semantic_layer_schema import Relation, SemanticLayerSchema


class QueryBuilder:
    def __init__(self, schema: SemanticLayerSchema):
        self.schema = schema

    def format_query(self, query):
        return query

    def build_query(self) -> str:
        columns = self._get_columns()
        query = f"SELECT {columns}"
        query += self._get_from_statement()
        query += self._add_group_by()
        query += self._add_order_by()
        query += self._add_limit()

        return query

    def _get_columns(self) -> str:
        if not self.schema.columns:
            return "*"

        column_parts = []
        for col in self.schema.columns:
            if col.expression:
                column_parts.append(f"{col.expression} as {col.name}")
            else:
                column_parts.append(col.name)

        return ", ".join(column_parts)

    def _get_from_statement(self):
        return f" FROM {self.schema.source.table.lower()}"

    def _add_group_by(self) -> str:
        if not self.schema.group_by:
            return ""

        group_by_cols = []
        for col_name in self.schema.group_by:
            # Find if this column has a transformation
            col = next((c for c in self.schema.columns if c.name == col_name), None)
            if col and col.expression and "case when" in col.expression.lower():
                # If it's a CASE expression, we need to group by the full expression
                group_by_cols.append(col.expression)
            else:
                group_by_cols.append(col_name)

        return f" GROUP BY {', '.join(group_by_cols)}"

    def _add_order_by(self) -> str:
        if not self.schema.order_by:
            return ""

        order_by = self.schema.order_by
        order_by_clause = self._format_order_by(order_by)
        return f" ORDER BY {order_by_clause}"

    @staticmethod
    def _format_order_by(order_by: List[str]) -> str:
        return ", ".join(order_by)

    def _add_limit(self, n=None) -> str:
        limit = n or self.schema.limit
        return f" LIMIT {limit}" if limit else ""

    def get_head_query(self, n=5):
        source_type = self.schema.source.type
        columns = self._get_columns()
        query = f"SELECT {columns}"
        query += self._get_from_statement()
        order_by = "RANDOM()" if source_type in {"sqlite", "postgres"} else "RAND()"
        return f"{query} ORDER BY {order_by} LIMIT {n}"

    def get_row_count(self):
        return f"SELECT COUNT(*) {self._get_from_statement()}"
