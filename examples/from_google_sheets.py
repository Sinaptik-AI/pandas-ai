"""Example of using PandasAI with am Excel file."""

from pandasai import PandasAI
from pandasai.helpers import from_google_sheets
from pandasai.llm import OpenAI

# Betas & Bludgers Writing Competitions List (source: https://heystacks.com/?type=sheets&tags=data)
dfs = from_google_sheets(
    "https://docs.google.com/spreadsheets/d/1VKkhugv2eF87AoOm4OXjI0sQEHrNhxy6gPL3F7xyw7g/edit#gid=115719017"
)

llm = OpenAI()
pandas_ai = PandasAI(llm, verbose=True)
response = pandas_ai(dfs, "How many short stories are there?")
print(response)
# Output: 35
