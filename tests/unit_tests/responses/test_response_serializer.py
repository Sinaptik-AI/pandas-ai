import unittest

import pandas as pd

from pandasai.responses.response_serializer import ResponseSerializer


class TestResponseSerializer(unittest.TestCase):
    def setUp(self) -> None:
        self.serializer = ResponseSerializer()
        self.df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        self.series = pd.Series([1, 2, 3])
        self.response_type_df = {"type": "dataframe", "value": self.df}
        self.response_type_series = {"type": "dataframe", "value": self.series}
        self.response_type_plot = {"type": "plot", "value": "path_to_image.png"}

    def test_serialize_dataframe(self) -> None:
        result = self.serializer.serialize_dataframe(self.df)
        self.assertEqual(result["headers"], list(self.df.columns))
        self.assertEqual(result["rows"], self.df.values.tolist())

    def test_serialize_dataframe_from_series(self) -> None:
        result = self.serializer.serialize(self.response_type_series)
        self.assertEqual(
            result["value"]["headers"], list(self.series.to_frame().columns)
        )
        self.assertEqual(
            result["value"]["rows"], self.series.to_frame().values.tolist()
        )

    def test_serialize_dataframe_from_df(self) -> None:
        result = self.serializer.serialize(self.response_type_df)
        self.assertEqual(result["value"]["headers"], list(self.df.columns))
        self.assertEqual(result["value"]["rows"], self.df.values.tolist())
