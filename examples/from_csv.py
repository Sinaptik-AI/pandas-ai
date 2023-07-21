"""Example of using PandasAI with a CSV file."""

import pandas as pd

from pandasai.smart_dataframe import SmartDataframe
from pandasai.llm.openai import OpenAI

df = pd.read_csv("examples/data/Loan payments data.csv")

llm = OpenAI()
df = SmartDataframe("examples/data/Loan payments data.xlsx", config={"llm": llm})
response = df.chat("How many loans are from men and have been paid off?")
print(response)
# Output: 247 loans have been paid off by men.
