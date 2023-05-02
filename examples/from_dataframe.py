"""Example of using PandasAI with a Pandas DataFrame"""

from data.sample_dataframe import dataframe
import pandas as pd
from pandasai import PandasAI
from pandasai.llm.openai import OpenAI

df = pd.DataFrame(dataframe)

llm = OpenAI()
pandas_ai = PandasAI(llm, verbose=True, conversational=False)
response = pandas_ai.run(df, "Calculate the sum of the gdp of north american countries")
print(response)
# Output: 26200000
