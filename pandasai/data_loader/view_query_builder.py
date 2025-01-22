from typing import Any, Dict, List, Union

from pandasai.data_loader.query_builder import QueryBuilder
from pandasai.data_loader.semantic_layer_schema import Relation, SemanticLayerSchema


class ViewQueryBuilder(QueryBuilder):
    def __init__(self, schema: SemanticLayerSchema):
        super().__init__(schema)

    def format_query(self, query):
        return f"{self._get_with_statement()}{query}"

    def build_query(self) -> str:
        columns = self._get_columns()
        query = self._get_with_statement()
        query += f"SELECT {columns}"
        query += self._get_from_statement()
        query += self._add_order_by()
        query += self._add_limit()
        return query

    def _get_columns(self) -> str:
        if self.schema.columns:
            return ", ".join(
                [f"{col.name.replace('.', '_')}" for col in self.schema.columns]
            )
        else:
            return super()._get_columns()

    def _get_from_statement(self):
        return f" FROM {self.schema.name}"

    def _get_with_statement(self):
        relations = self.schema.relations
        first_table = relations[0].from_.split(".")[0]
        query = f"WITH {self.schema.name} AS ( SELECT\n"

        if self.schema.columns:
            query += ", ".join(
                [
                    f"{col.name} AS {col.name.replace('.', '_')}"
                    for col in self.schema.columns
                ]
            )
        else:
            query += "*"

        query += f"\nFROM {first_table}"
        for relation in relations:
            to_table = relation.to.split(".")[0]
            query += f"\nJOIN {to_table} ON {relation.from_} = {relation.to}"
        query += ")\n"
        return query
