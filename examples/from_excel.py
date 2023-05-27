"""Example of using PandasAI with am Excel file."""

from pandasai import PandasAI
from pandasai.helpers.from_excel import from_excel
from pandasai.llm.openai import OpenAI

df = from_excel("examples/data/Loan payments data.xlsx")

llm = OpenAI()
pandas_ai = PandasAI(llm, verbose=True)
response = pandas_ai(df, "How many loans are from men and have been paid off?")
print(response)
# Output: 247 loans have been paid off by men.
