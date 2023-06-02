"""Example of using PandasAI with a Pandas DataFrame"""

import pandas as pd

from pandasai import PandasAI
from pandasai.llm.openai import OpenAI

from data.sample_dataframe import dataframe

df = pd.DataFrame(dataframe)

llm = OpenAI()
pandas_ai = PandasAI(llm, verbose=True, conversational=False)
response = pandas_ai(df, "Calculate the sum of the gdp of north american countries")
print(response)
# Output: 20901884461056

# Dataframe is returned
response = pandas_ai(df, "Filter the dataframe to show only countries with happiness index greater than 6.0")
print(f'Response type::{type(response)}')
print(response)