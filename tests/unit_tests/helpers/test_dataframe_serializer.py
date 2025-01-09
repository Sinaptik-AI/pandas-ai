import unittest

from pandasai.dataframe.base import DataFrame
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
        connector = DataFrame(data, name="en_table_name", description="中文_描述")
        result = self.serializer.serialize(
            connector,
            type_=DataframeSerializerType.YML,
            extras={"index": 0, "type": "pd.Dataframe"},
        )
        print(result)
        self.assertIn(
            """dfs[0]:
  name: en_table_name
  description: null
  type: pd.Dataframe
  rows: 2
  columns: 1
  schema:
    fields:
    - name: name
      type: object
""",
            result,
        )
