"""Example of using PandasAI with am Excel file."""

from pandasai import SmartDataframe
from pandasai.llm import OpenAI

# Betas & Bludgers Writing Competitions List (source: https://heystacks.com/?type=sheets&tags=data)
google_sheets_url = "https://docs.google.com/spreadsheets/d/1VKkhugv2eF87AoOm4OXjI0sQEHrNhxy6gPL3F7xyw7g/edit#gid=115719017"  # noqa E501

llm = OpenAI()
df = SmartDataframe(google_sheets_url, config={"llm": llm})
response = df.chat("How many short stories are there?")
print(response)
# Output: 35
