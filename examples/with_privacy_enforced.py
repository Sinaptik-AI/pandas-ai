"""Example of using PandasAI with a Pandas DataFrame"""

import pandas as pd

from pandasai import SmartDataframe
from pandasai.llm import OpenAI

from .data.sample_dataframe import dataframe

llm = OpenAI()
df = SmartDataframe(
    df=pd.DataFrame(dataframe), config={"llm": llm, "enforce_privacy": True}
)
response = df.chat("Calculate the sum of the gdp of north american countries")
print(response)
# Output: 20901884461056
