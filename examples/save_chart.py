"""Example of using PandasAI to generate and save a chart from a Pandas DataFrame"""

import os

import pandas as pd
from data.sample_dataframe import dataframe

from pandasai import SmartDataframe
from pandasai.helpers import path
from pandasai.llm import OpenAI

df = pd.DataFrame(dataframe)

llm = OpenAI()

try:
    user_defined_path = path.find_project_root()
except ValueError:
    user_defined_path = os.getcwd()

user_defined_path = os.path.join(user_defined_path, "exports", "charts")
df = SmartDataframe(
    df,
    config={
        "llm": llm,
        "save_charts_path": user_defined_path,
        "save_charts": True,
        "verbose": True,
    },
)
response = df.chat(
    "Plot the histogram of countries showing for each the gpd,"
    " using different colors for each bar",
)
# Output: check out $pwd/exports/charts/{hashid}/chart.png
