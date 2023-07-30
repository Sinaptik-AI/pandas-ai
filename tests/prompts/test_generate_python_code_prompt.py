"""Unit tests for the generate python code prompt class"""


import pandas as pd
from pandasai.smart_dataframe import SmartDataframe
from pandasai.prompts.generate_python_code import GeneratePythonCodePrompt


class TestGeneratePythonCodePrompt:
    """Unit tests for the generate python code prompt class"""

    def test_str_with_args(self):
        """Test that the __str__ method is implemented"""

        dfs = [
            SmartDataframe(
                pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]}),
                config={"anonymize_dataframe": False},
            )
        ]
        assert (
            str(
                GeneratePythonCodePrompt(
                    engine="pandas", conversation="Question", dfs=dfs
                )
            )
            == """
You are provided with the following pandas DataFrames with the following metadata:

Dataframe dfs[0], with 3 rows and 2 columns.
This is the metadata of the dataframe dfs[0]:
a,b
1,4
2,5
3,6


Here is a placeholder Python code with a clear structure and naming convention based on the phases of data analysis. Your task is to generate the specific code within this template and ensure the requested python code is prefixed with <startCode> exactly and suffix the code with <endCode> exactly.

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
Question
"""  # noqa: E501
        )
