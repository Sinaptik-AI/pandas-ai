"""Example of using PandasAI with am Excel file."""

from pandasai import SmartDataframe
from pandasai.llm import OpenAI

llm = OpenAI()

df = SmartDataframe("examples/data/Loan payments data.xlsx", config={"llm": llm})
response = df.chat("How many loans are from men and have been paid off?")
print(response)
# Output: 247 loans have been paid off by men.
