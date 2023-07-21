"""Example of using PandasAI with a Pandas DataFrame"""

import pandas as pd
from data.sample_dataframe import dataframe

from pandasai.smart_dataframe import SmartDataframe
from pandasai.llm.openai import OpenAI

df = pd.DataFrame(dataframe)

llm = OpenAI()
df = SmartDataframe(
    df=pd.DataFrame(dataframe),
    name="Countries",
    description="A dataframe with countries with their GDPs and happiness scores",
    config={"llm": llm},
)
response = df.chat("Calculate the sum of the gdp of north american countries")
print(response)
print(df.last_prompt)
# Output: 20901884461056
