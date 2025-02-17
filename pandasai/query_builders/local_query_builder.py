import os

from .. import ConfigManager
from ..data_loader.semantic_layer_schema import SemanticLayerSchema
from .base_query_builder import BaseQueryBuilder


class LocalQueryBuilder(BaseQueryBuilder):
    def __init__(self, schema: SemanticLayerSchema, dataset_path: str):
        super().__init__(schema)
        self.dataset_path = dataset_path

    def _get_table_expression(self) -> str:
        filemanager = ConfigManager.get().file_manager
        filepath = os.path.join(
            self.dataset_path,
            self.schema.source.path,
        )
        abspath = filemanager.abs_path(filepath)
        source_type = self.schema.source.type

        if source_type == "parquet":
            return f"read_parquet('{abspath}')"
        elif source_type == "csv":
            return f"read_csv('{abspath}')"
        else:
            raise ValueError(f"Unsupported file format: {source_type}")
