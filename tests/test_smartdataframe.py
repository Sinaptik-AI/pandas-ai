"""Unit tests for the SmartDatalake class"""
import json
import os
from typing import Optional
from unittest.mock import patch, Mock

import pandas as pd
from pydantic import BaseModel, Field
import pytest

from pandasai import SmartDataframe
from pandasai.exceptions import LLMNotFoundError
from pandasai.llm.fake import FakeLLM


class TestSmartDataframe:
    """Unit tests for the SmartDatalake class"""

    def tearDown(self):
        for filename in [
            "df_test.parquet",
            "df_duplicate.parquet",
        ]:
            if os.path.exists("cache/" + filename):
                os.remove("cache/" + filename)

        # Remove saved_dfs from pandasai.json
        with open("pandasai.json", "r") as json_file:
            data = json.load(json_file)
            data["saved_dfs"] = []
        with open("pandasai.json", "w") as json_file:
            json.dump(data, json_file, indent=2)

    @pytest.fixture
    def llm(self, output: Optional[str] = None):
        return FakeLLM(output=output)

    @pytest.fixture
    def data_sampler(self):
        class DataSampler:
            df = None

            def __init__(self, df: pd.DataFrame):
                self.df = df

            def sample(self, _n: int = 5):
                return self.df

        return DataSampler

    @pytest.fixture
    def sample_df(self):
        return pd.DataFrame(
            {
                "country": [
                    "United States",
                    "United Kingdom",
                    "France",
                    "Germany",
                    "Italy",
                    "Spain",
                    "Canada",
                    "Australia",
                    "Japan",
                    "China",
                ],
                "gdp": [
                    19294482071552,
                    2891615567872,
                    2411255037952,
                    3435817336832,
                    1745433788416,
                    1181205135360,
                    1607402389504,
                    1490967855104,
                    4380756541440,
                    14631844184064,
                ],
                "happiness_index": [
                    6.94,
                    7.16,
                    6.66,
                    7.07,
                    6.38,
                    6.4,
                    7.23,
                    7.22,
                    5.87,
                    5.12,
                ],
            }
        )

    @pytest.fixture
    def custom_head(self, sample_df: pd.DataFrame):
        return pd.DataFrame({"A": [1, 2, 3, 4], "B": [5, 6, 7, 8]})

    @pytest.fixture
    def smart_dataframe(self, llm, sample_df, custom_head):
        return SmartDataframe(
            sample_df,
            config={"llm": llm, "enable_cache": False},
            custom_head=custom_head,
        )

    @pytest.fixture
    def llm_result_mocks(self, custom_head):
        result_template = "result = {{ 'type': '{type}', 'value': {value} }}"

        return {
            "number": result_template.format(type="number", value=1),
            "string": result_template.format(type="string", value="'Test'"),
            "plot": result_template.format(type="plot", value="'temp_plot.png'"),
            "dataframe": result_template.format(type="dataframe", value=custom_head),
        }

    @pytest.fixture
    def smart_dataframe_mocked_df(self, llm, sample_df, custom_head):
        smart_df = SmartDataframe(
            sample_df,
            config={"llm": llm, "enable_cache": False},
            custom_head=custom_head,
        )
        smart_df._core._df = Mock()
        return smart_df

    def test_init(self, smart_dataframe):
        assert smart_dataframe.table_name is None
        assert smart_dataframe.table_description is None
        assert smart_dataframe.dataframe is None

    def test_init_without_llm(self, sample_df):
        with pytest.raises(LLMNotFoundError):
            SmartDataframe(sample_df, config={"llm": "-"})

    def test_extract_code(self, llm):
        code = """```python
result = {'happiness': 0.5, 'gdp': 0.8}
print(result)```"""
        assert (
            llm._extract_code(code)
            == "result = {'happiness': 0.5, 'gdp': 0.8}\nprint(result)"
        )

        code = """```
result = {'happiness': 1, 'gdp': 0.43}```"""
        assert llm._extract_code(code) == "result = {'happiness': 1, 'gdp': 0.43}"

    def test_custom_head_getter(self, custom_head, smart_dataframe: SmartDataframe):
        assert smart_dataframe.head_df.custom_head.equals(custom_head)

    def test_custom_head_setter(self, custom_head, smart_dataframe: SmartDataframe):
        new_custom_head = (
            custom_head.copy().sample(frac=1, axis=1).reset_index(drop=True)
        )
        smart_dataframe.head_df.custom_head = new_custom_head
        assert new_custom_head.equals(smart_dataframe.head_df.custom_head)

    def test_pydantic_validate(self, llm):
        # Create a sample DataFrame
        df = pd.DataFrame({"A": [1, 2, 3, 4], "B": [5, 6, 7, 8]})

        # Create an instance of SmartDataframe without a name
        df_object = SmartDataframe(
            df, description="Name", config={"llm": llm, "enable_cache": False}
        )

        # Pydantic Schema
        class TestSchema(BaseModel):
            A: int
            B: int

        validation_result = df_object.validate(TestSchema)

        assert validation_result.passed

    def test_pydantic_validate_false(self, llm):
        # Create a sample DataFrame
        df = pd.DataFrame({"A": ["Test", "Test2", "Test3", "Test4"], "B": [5, 6, 7, 8]})

        # Create an instance of SmartDataframe without a name
        df_object = SmartDataframe(
            df, description="Name", config={"llm": llm, "enable_cache": False}
        )

        # Pydantic Schema
        class TestSchema(BaseModel):
            A: int
            B: int

        validation_result = df_object.validate(TestSchema)

        assert validation_result.passed is False

    def test_pydantic_validate_false_one_record(self, llm):
        # Create a sample DataFrame
        df = pd.DataFrame({"A": [1, "test", 3, 4], "B": [5, 6, 7, 8]})

        # Create an instance of SmartDataframe without a name
        df_object = SmartDataframe(
            df, description="Name", config={"llm": llm, "enable_cache": False}
        )

        # Pydantic Schema
        class TestSchema(BaseModel):
            A: int
            B: int

        validation_result = df_object.validate(TestSchema)
        assert (
            validation_result.passed is False and len(validation_result.errors()) == 1
        )

    def test_pydantic_validate_complex_schema(self, llm):
        # Create a sample DataFrame
        df = pd.DataFrame({"A": [1, 2, 3, 4], "B": [5, 6, 7, 8]})

        # Create an instance of SmartDataframe without a name
        df_object = SmartDataframe(
            df, description="Name", config={"llm": llm, "enable_cache": False}
        )

        # Pydantic Schema
        class TestSchema(BaseModel):
            A: int = Field(..., gt=5)
            B: int

        validation_result = df_object.validate(TestSchema)

        assert validation_result.passed is False

        class TestSchema(BaseModel):
            A: int = Field(..., lt=5)
            B: int

        validation_result = df_object.validate(TestSchema)

        assert validation_result.passed

    def test_head_csv_with_custom_head(
        self, custom_head, data_sampler, smart_dataframe: SmartDataframe
    ):
        with patch("pandasai.connectors.pandas.PandasConnector", new=data_sampler):
            assert smart_dataframe.head_df.to_csv() == custom_head.to_csv(index=False)
