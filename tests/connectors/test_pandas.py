import pandas as pd
from pandasai.connectors import PandasConnector


class TestPandasConnector:
    def test_load_dataframe_from_list(self):
        input_data = [
            {"column1": 1, "column2": 4},
            {"column1": 2, "column2": 5},
            {"column1": 3, "column2": 6},
        ]
        connector = PandasConnector({"original_df": input_data})
        assert isinstance(connector.execute(), pd.DataFrame)

    def test_load_dataframe_from_dict(self):
        input_data = {"column1": [1, 2, 3], "column2": [4, 5, 6]}
        connector = PandasConnector({"original_df": input_data})
        assert isinstance(connector.execute(), pd.DataFrame)

    def test_load_dataframe_from_pandas_dataframe(self):
        input_data = pd.DataFrame({"column1": [1, 2, 3], "column2": [4, 5, 6]})
        connector = PandasConnector({"original_df": input_data})
        assert isinstance(connector.execute(), pd.DataFrame)

    def test_import_pandas_series(self):
        input_data = pd.Series([1, 2, 3])
        connector = PandasConnector({"original_df": input_data})
        assert isinstance(connector.execute(), pd.DataFrame)
