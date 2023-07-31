"""Unit tests for the generate python code prompt class"""


from pandasai.prompts import GeneratePythonCodePrompt


class TestGeneratePythonCodePrompt:
    """Unit tests for the generate python code prompt class"""

    def test_str_with_args(self):
        """Test that the __str__ method is implemented"""
        assert (
            str(
                GeneratePythonCodePrompt(
                    df_head="df.head()",
                    num_rows=10,
                    num_columns=5,
                )
            )
            == """
You are provided with a pandas dataframe (df) with 10 rows and 5 columns.
This is the metadata of the dataframe:
df.head().

When asked about the data, your response should include a python code that describes the dataframe `df`.
Using the provided dataframe, df, return the python code and make sure to prefix the requested python code with <startCode> exactly and suffix the code with <endCode> exactly to get the answer to the following question:
"""  # noqa: E501
        )
