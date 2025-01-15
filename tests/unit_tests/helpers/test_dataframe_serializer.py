import pytest

from pandasai import DataFrame
from pandasai.helpers.dataframe_serializer import DataframeSerializer


class TestDataframeSerializer:
    @pytest.fixture
    def sample_df(self):
        df = DataFrame({"Name": ["Alice", "Bob"], "Age": [25, 30]})
        df.name = "test_table"
        df.description = "This is a test table"
        return df

    @pytest.fixture
    def sample_dataframe_serializer(self):
        return DataframeSerializer()

    def test_serialize_with_name_and_description(
        self, sample_dataframe_serializer, sample_df
    ):
        """Test serialization with name and description attributes."""

        result = sample_dataframe_serializer.serialize(sample_df)
        expected = """<table table_name="test_table" description="This is a test table" dimensions="2x2">
Name,Age
Alice,25
Bob,30
</table>
"""
        assert result.replace("\r\n", "\n") == expected.replace("\r\n", "\n")
