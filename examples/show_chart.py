"""Example of using PandasAI to generate a chart from a Pandas DataFrame"""

import pandas as pd
from data.sample_dataframe import dataframe

from pandasai import PandasAI
from pandasai.llm import OpenAI

df = pd.DataFrame(dataframe)

llm = OpenAI()
pandas_ai = PandasAI(llm, verbose=True)
response = pandas_ai(
    df,
    "Plot the histogram of countries showing for each the gpd,"
    " using different colors for each bar",
)
# Output: check out images/histogram-chart.png
