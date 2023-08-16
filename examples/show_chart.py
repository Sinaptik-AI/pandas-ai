"""Example of using PandasAI to generate a chart from a Pandas DataFrame"""

import pandas as pd
from data.sample_dataframe import dataframe

from pandasai import SmartDataframe
from pandasai.llm import OpenAI

df = pd.DataFrame(dataframe)

llm = OpenAI()
df = SmartDataframe(df, config={"llm": llm, "verbose": True})
response = df.chat(
    "Plot the histogram of countries showing for each the gpd,"
    " using different colors for each bar",
)
# Output: check out images/histogram-chart.png
