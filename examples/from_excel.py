"""Example of using PandasAI with am Excel file."""

import os

from pandasai import Agent

# Get your FREE API key signing up at https://pandabi.ai.
# You can also configure it in your .env file.
os.environ["PANDASAI_API_KEY"] = "your-api-key"

agent = Agent("examples/data/Loan payments data.xlsx")
response = agent.chat("How many loans are from men and have been paid off?")
print(response)
# Output: 247 loans have been paid off by men.
