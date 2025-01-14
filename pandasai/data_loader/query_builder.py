from typing import Any, Dict, List, Union

from pandasai.data_loader.semantic_layer_schema import SemanticLayerSchema


class QueryBuilder:
    def __init__(self, schema: SemanticLayerSchema):
        self.schema = schema

    def build_query(self) -> str:
        columns = self._get_columns()
        table_name = self._get_table_name()
        query = f"SELECT {columns} FROM {table_name}"

        query += self._add_order_by()
        query += self._add_limit()

        return query

    def _get_columns(self) -> str:
        if self.schema.columns:
            return ", ".join([col.name for col in self.schema.columns])
        else:
            return "*"

    def _get_table_name(self):
        table_name = self.schema.source.table
        table_name = table_name.lower()
        return table_name

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
        table_name = self._get_table_name()
        columns = self._get_columns()

        order_by = "RANDOM()" if source_type in {"sqlite", "postgres"} else "RAND()"

        return f"SELECT {columns} FROM {table_name} ORDER BY {order_by} LIMIT {n}"

    def get_row_count(self):
        table_name = self._get_table_name()
        return f"SELECT COUNT(*) FROM {table_name}"
