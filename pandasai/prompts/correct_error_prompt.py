""" Prompt to correct Python Code on Error
```
You are provided with a pandas dataframe (df) with {num_rows} rows and {num_columns} columns.
This is the metadata of the dataframe:
{df_head}.

The user asked the following question:
{question}

You generated this python code:
{code}

It fails with the following error:
{error_returned}

Correct the python code and return a new python code (do not import anything) that fixes the above
mentioned error. Do not generate the same code again.
```
"""  # noqa: E501

from .base import Prompt


class CorrectErrorPrompt(Prompt):
    """Prompt to Correct Python code on Error"""

    text: str = """
You are provided with the following {engine} DataFrames with the following metadata:

{dataframes}

The user asked the following question:
{conversation}

You generated this python code:
{code}

It fails with the following error:
{error_returned}

Correct the python code and return a new python code (do not import anything) that fixes the above mentioned error. Do not generate the same code again.
"""  # noqa: E501

    def __init__(self, **kwargs):
        dataframes = []
        for index, df in enumerate(kwargs["dfs"], start=1):
            description = "Dataframe "
            if df.table_name is not None:
                description += f'"{df.table_name}" (dfs[{index-1}])'
            else:
                description += f"dfs[{index-1}]"
            description += (
                f", with {df.rows_count} rows and {df.columns_count} columns."
            )
            if df.table_description is not None:
                description += f"\nDescription: {df.table_description}"
            description += f"""
This is the metadata of the dataframe dfs[{index-1}]:
{df.head_csv}"""  # noqa: E501
            dataframes.append(description)

        super().__init__(
            **kwargs,
            dataframes="\n\n".join(dataframes),
        )
