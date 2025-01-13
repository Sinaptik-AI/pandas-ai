"""Example of using PandaAI with a Parquet file."""

import os

from pandasai import Agent

# By default, unless you choose a different LLM, it will use BambooLLM.
# You can get your free API key signing up at https://pandabi.ai (you can also configure it in your .env file)
os.environ["PANDABI_API_KEY"] = "YOUR_PANDABI_API_KEY"

agent = Agent("examples/data/Loan payments data.parquet")
response = agent.chat("How many loans are from men and have been paid off?")
print(response)
# Output: 247 loans have been paid off by men.
