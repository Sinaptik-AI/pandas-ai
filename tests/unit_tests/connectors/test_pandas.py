import pandasai.pandas as pd
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

    def test_to_json(self):
        input_data = pd.DataFrame(
            {
                "EmployeeID": [1, 2, 3, 4, 5],
                "Name": ["John", "Emma", "Liam", "Olivia", "William"],
                "Department": ["HR", "Sales", "IT", "Marketing", "Finance"],
            }
        )
        connector = PandasConnector({"original_df": input_data})
        data = connector.to_json()

        assert isinstance(data, dict)
        assert "name" in data
        assert "description" in data
        assert "head" in data
        assert isinstance(data["head"], list)

    def test_type_name_property(self):
        input_data = [
            {"column1": 1, "column2": 4},
            {"column1": 2, "column2": 5},
            {"column1": 3, "column2": 6},
        ]
        connector = PandasConnector({"original_df": input_data})
        assert connector.type == "pd.DataFrame"
