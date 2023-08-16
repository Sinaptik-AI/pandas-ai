"""Example of using PandasAI with a Pandas DataFrame"""

import pandas as pd
from data.sample_dataframe import dataframe

from pandasai import SmartDataframe
from pandasai.llm import OpenAI

df = pd.DataFrame(dataframe)

llm = OpenAI()
df = SmartDataframe(df=pd.DataFrame(dataframe), config={"llm": llm})
response = df.chat("Calculate the sum of the gdp of north american countries")
print(response)
# Output: 20901884461056
