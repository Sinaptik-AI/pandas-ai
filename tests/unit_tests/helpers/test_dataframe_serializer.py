import unittest

import pandas as pd

from pandasai.connectors import PandasConnector
from pandasai.helpers.dataframe_serializer import (
    DataframeSerializer,
    DataframeSerializerType,
)


class TestDataframeSerializer(unittest.TestCase):
    def setUp(self):
        self.serializer = DataframeSerializer()

    def test_convert_df_to_yml(self):
        # Test convert df to yml
        data = {"name": ["en_name", "中文_名称"]}
        connector = PandasConnector(
            {"original_df": pd.DataFrame(data)},
            name="en_table_name",
            description="中文_描述",
            field_descriptions={k: k for k in data},
        )
        result = self.serializer.serialize(
            connector,
            type_=DataframeSerializerType.YML,
            extras={"index": 0, "type": "pd.Dataframe"},
        )
        self.assertIn("中文_描述", result)
