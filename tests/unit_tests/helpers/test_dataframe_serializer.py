from pandasai.helpers.dataframe_serializer import DataframeSerializer


class TestDataframeSerializer:
    def test_serialize_with_name_and_description(self, sample_df):
        """Test serialization with name and description attributes."""

        result = DataframeSerializer.serialize(sample_df)
        expected = """<table dialect="postgres" table_name="table_6c30b42101939c7bdf95f4c1052d615c" dimensions="3x2">
A,B
1,4
2,5
3,6
</table>
"""
        assert result.replace("\r\n", "\n") == expected.replace("\r\n", "\n")

    def test_serialize_with_name_and_description_with_dialect(self, sample_df):
        """Test serialization with name and description attributes."""

        result = DataframeSerializer.serialize(sample_df, dialect="mysql")
        expected = """<table dialect="mysql" table_name="table_6c30b42101939c7bdf95f4c1052d615c" dimensions="3x2">
A,B
1,4
2,5
3,6
</table>
"""
        assert result.replace("\r\n", "\n") == expected.replace("\r\n", "\n")
