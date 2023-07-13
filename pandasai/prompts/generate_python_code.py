""" Prompt to generate Python code
```
Today is {today_date}.
You are provided with a pandas dataframe (df) with {num_rows} rows and {num_columns} columns.
This is the metadata of the dataframe:
{df_head}.

When asked about the data, your response should include a python code that describes the
dataframe `df`. Using the provided dataframe, df, return the python code to get the answer to the following question:
```
"""  # noqa: E501

from datetime import date

from .base import Prompt
from ..constants import START_CODE_TAG, END_CODE_TAG


class GeneratePythonCodePrompt(Prompt):
    """Prompt to generate Python code"""

    text: str = """
Date: {today_date}
You are provided with the following {engine} DataFrames with the following metadata:

{dataframes}

Here is a placeholder Python code with a clear structure and naming convention based on the phases of data analysis. Your task is to generate the specific code within this template and ensure the requested python code is prefixed with {START_CODE_TAG} exactly and suffix the code with {END_CODE_TAG} exactly.

# The Python code should be structured as follows:

#TODO: Import any necessary libraries

class DataFrameAnalysis:
    def __init__(self, dfs: list):
        self.dfs: list = dfs.copy()  # To ensure the original dfs are not modified in place
        self.df_output = []  # An array to store multiple outputs (possible types: text, plot, dataframe)
        self.df_output.append(dict(type = "dataframe", result = self.dfs))  # Add the initial dataframes as the first output
        # TODO: Add additional items to the df_output list as necessary to support other output types such as plots, etc.

    # 1. Prepare: Preprocessing and cleaning data if necessary
    def prepare_data(self):
        # TODO: Insert your generated Python code here

    # 2. Process: Manipulating data for analysis (grouping, filtering, aggregating, etc.)
    def process_data(self):
        # TODO: Insert your generated Python code here

    # 3. Analyze: Conducting the actual analysis
    def analyze_data(self):
        # TODO: Insert your generated Python code here
        # If generating a plot, create a figure and axes using plt.subplots() and
        # save it to an image in exports/charts/temp_chart.png and do not show the chart
        # Any output should be added to the df_output list.

    # 4. Output: Returning the result in a standardized format
    def output_data(self):
        # TODO: Insert your generated Python code here
        # TODO: Set the result type and value in the df_output dictionary. The result could be a DataFrame, plot, etc.

        return self.df_output

    def run(self):
        self.prepare_data()
        self.process_data()
        self.analyze_data()
        return self.output_data()

# The following code should be outside the class definition and remain unchanged
analysis = DataFrameAnalysis(dfs)
result = analysis.run()

Using the provided DataFrames, please generate the specific Python code to be inserted into the respective methods in order to answer the following question:
"""  # noqa: E501

    def __init__(self, **kwargs):
        dataframes = ""
        for index, df in enumerate(kwargs["dfs"], start=1):
            dataframes += f"""Dataframe dfs[{index-1}], with {df["num_rows"]} rows and {df["num_columns"]} columns.
This is the metadata of the dataframe dfs[{index-1}]:
{df["df_head"]}

"""  # noqa: E501

        super().__init__(
            **kwargs,
            today_date=date.today(),
            START_CODE_TAG=START_CODE_TAG,
            END_CODE_TAG=END_CODE_TAG,
            dataframes=dataframes,
        )
