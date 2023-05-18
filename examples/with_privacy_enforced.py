"""Example of using PandasAI with a Pandas DataFrame"""

import pandas as pd

from pandasai import PandasAI
from pandasai.llm.openai import OpenAI

from .data.sample_dataframe import dataframe

df = pd.DataFrame(dataframe)

llm = OpenAI()
pandas_ai = PandasAI(llm, verbose=True, conversational=False, enforce_privacy=True)
response = pandas_ai(
    df,
    "Calculate the sum of the gdp of north american countries",
)
print(response)
# Output: 20901884461056
