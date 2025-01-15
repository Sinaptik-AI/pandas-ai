import pandasai as pai
from pandasai.data_loader.semantic_layer_schema import SemanticLayerSchema

df = pai.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})

schema = SemanticLayerSchema(
    **{
        "name": "test",
        "description": "test",
        "source": {"type": "parquet", "path": "data.parquet"},
        "columns": [
            {
                "name": "a",
            },
            {
                "name": "b",
            },
        ],
    }
)

print(pai.create("test/test", df, schema))
