from typing import Dict

from sqlglot import exp, expressions, parse_one, select
from sqlglot.expressions import Subquery

from ..data_loader.loader import DatasetLoader
from ..data_loader.semantic_layer_schema import SemanticLayerSchema
from ..helpers.sql_sanitizer import sanitize_relation_name
from .base_query_builder import BaseQueryBuilder


class ViewQueryBuilder(BaseQueryBuilder):
    def __init__(
        self,
        schema: SemanticLayerSchema,
        schema_dependencies_dict: Dict[str, DatasetLoader],
    ):
        super().__init__(schema)
        self.schema_dependencies_dict = schema_dependencies_dict

    def _get_columns(self) -> list[str]:
        if self.schema.columns:
            return [col.name.replace(".", "_") for col in self.schema.columns]
        else:
            return super()._get_columns()

    def _get_sub_query_from_loader(self, loader: DatasetLoader) -> Subquery:
        sub_query = parse_one(loader.query_builder.build_query())
        return exp.Subquery(this=sub_query, alias=loader.schema.name)

    def _get_table_expression(self) -> str:
        relations = self.schema.relations
        first_dataset = relations[0].from_.split(".")[0]
        first_loader = self.schema_dependencies_dict[first_dataset]
        first_query = self._get_sub_query_from_loader(first_loader)

        if self.schema.columns:
            columns = [
                f"{col.name} AS {col.name.replace('.', '_')}"
                for col in self.schema.columns
            ]
        else:
            columns = ["*"]

        # query = select(*columns).from_(first_query).sql(pretty=True)
        query = select(*columns).from_(first_query)

        for relation in relations:
            to_datasets = relation.to.split(".")[0]
            loader = self.schema_dependencies_dict[to_datasets]
            subquery = self._get_sub_query_from_loader(loader)
            query = query.join(
                subquery,
                on=f"{sanitize_relation_name(relation.from_)} = {sanitize_relation_name(relation.to)}",
                append=True,
            )

        return exp.Subquery(this=query, alias=self.schema.name).sql(pretty=True)
