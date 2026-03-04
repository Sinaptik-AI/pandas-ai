import pandas as pd
import pandasai as pai
from pandasai.data_loader.semantic_layer_schema import SemanticLayerSchema, Source


def test_schema_limit_applied_when_schema_assigned():
    """
    Test that SemanticLayerSchema.limit is applied when schema
    is assigned to a PandasAI DataFrame.
    """

    # create sample dataframe
    data = {
        "id": [1, 2, 3, 4, 5],
        "name": ["A", "B", "C", "D", "E"],
    }

    df = pai.DataFrame(pd.DataFrame(data))

    # create schema with limit
    schema = SemanticLayerSchema(
        name="data",
        source=Source(type="csv", path="dummy.csv"),
        limit=3,
    )

    # assign schema
    df.schema = schema

    # check limit applied
    assert len(df) == 3
