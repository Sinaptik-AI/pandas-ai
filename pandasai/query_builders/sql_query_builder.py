from .base_query_builder import BaseQueryBuilder


class SqlQueryBuilder(BaseQueryBuilder):
    def _get_from_statement(self):
        return f"FROM {self.schema.source.table.lower()}"
