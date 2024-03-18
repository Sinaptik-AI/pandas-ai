"""Example of using PandasAI with am Excel file."""

import os

from pandasai import Agent

# Betas & Bludgers Writing Competitions List (source: https://heystacks.com/?type=sheets&tags=data)
google_sheets_url = "https://docs.google.com/spreadsheets/d/1VKkhugv2eF87AoOm4OXjI0sQEHrNhxy6gPL3F7xyw7g/edit#gid=115719017"  # noqa E501

# Get your FREE API key signing up at https://pandabi.ai.
# You can also configure it in your .env file.
os.environ["PANDASAI_API_KEY"] = "your-api-key"

agent = Agent(google_sheets_url)
response = agent.chat("How many short stories are there?")
print(response)
# Output: 35
