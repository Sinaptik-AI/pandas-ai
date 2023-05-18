"""Example of using PandasAI with a CSV file."""

import pandas as pd

from pandasai import PandasAI
from pandasai.llm.openai import OpenAI

df = pd.read_csv("examples/data/Loan payments data.csv")

llm = OpenAI()
pandas_ai = PandasAI(llm, verbose=True)
response = pandas_ai(df, "How many loans are from men and have been paid off?")
print(response)
# Output: 247 loans have been paid off by men.
