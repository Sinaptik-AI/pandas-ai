"""Example of using PandasAI with am Excel file."""

import pandas as pd

from pandasai import PandasAI
from pandasai.helpers.from_excel import from_excel
from pandasai.llm.openai import OpenAI

# convert csv to xlsx for this example
df = pd.read_csv("examples/data/Loan payments data.csv")
df.to_excel("examples/data/Loan payments data.xlsx", index=False)

df = from_excel("examples/data/Loan payments data.xlsx")

llm = OpenAI()
pandas_ai = PandasAI(llm, verbose=True)
response = pandas_ai(df, "How many loans are from men and have been paid off?")
print(response)
# Output: 247 loans have been paid off by men.
