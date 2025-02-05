from .base_query_builder import BaseQueryBuilder


class SqlQueryBuilder(BaseQueryBuilder):
    def _get_table_expression(self) -> str:
        return self.schema.source.table.lower()
