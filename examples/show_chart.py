"""Example of using PandasAI to generate a chart from a Pandas DataFrame"""

import pandas as pd

from pandasai import PandasAI
from pandasai.llm.openai import OpenAI

from .data.sample_dataframe import dataframe

df = pd.DataFrame(dataframe)

llm = OpenAI()
pandas_ai = PandasAI(llm)
response = pandas_ai(
    df,
    "Plot the histogram of countries showing for each the gpd, using different colors for each bar",
)
print(response)
# Output: check out images/histogram-chart.png
