from typing import Any, Dict, List, Union


class QueryBuilder:
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema

    def build_query(self) -> str:
        columns = self._get_columns()
        table_name = self.schema["source"]["table"]
        query = f"SELECT {columns} FROM {table_name}"

        query += self._add_order_by()
        query += self._add_limit()

        return query

    def _get_columns(self) -> str:
        if "columns" in self.schema:
            return ", ".join([col["name"] for col in self.schema["columns"]])
        else:
            return "*"

    def _add_order_by(self) -> str:
        if "order_by" not in self.schema:
            return ""

        order_by = self.schema["order_by"]
        order_by_clause = self._format_order_by(order_by)
        return f" ORDER BY {order_by_clause}"

    def _format_order_by(self, order_by: Union[List[str], str]) -> str:
        return ", ".join(order_by) if isinstance(order_by, list) else order_by

    def _add_limit(self) -> str:
        return f" LIMIT {self.schema['limit']}" if "limit" in self.schema else ""
