from pandasai.dataframe.virtual_dataframe import VirtualDataFrame

from .semantic_layer_schema import SemanticLayerSchema
from .sql_loader import SQLDatasetLoader
from .view_query_builder import ViewQueryBuilder


class ViewDatasetLoader(SQLDatasetLoader):
    """
    Loader for view-based datasets.
    """

    def __init__(self, schema: SemanticLayerSchema, dataset_path: str):
        super().__init__(schema, dataset_path)
        self.query_builder: ViewQueryBuilder = ViewQueryBuilder(schema)

    def load(self) -> VirtualDataFrame:
        return VirtualDataFrame(
            schema=self.schema,
            data_loader=ViewDatasetLoader(self.schema, self.dataset_path),
            path=self.dataset_path,
        )
