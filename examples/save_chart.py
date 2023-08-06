"""Example of using PandasAI to generate and save a chart from a Pandas DataFrame"""

import pandas as pd
import os
from data.sample_dataframe import dataframe

from pandasai import PandasAI
from pandasai.llm import OpenAI
from pandasai.helpers import path

df = pd.DataFrame(dataframe)

llm = OpenAI()

try:
    user_defined_path = path.find_project_root()
except ValueError:
    user_defined_path = os.getcwd()
pandas_ai = PandasAI(
    llm, save_charts=True, save_charts_path=user_defined_path, verbose=True
)
response = pandas_ai(
    df,
    "Plot the histogram of countries showing for each the gpd,"
    " using different colors for each bar",
)
# Output: check out $pwd/exports/charts/{hashid}/chart.png
