import os

from pandasai import Agent

# By default, unless you choose a different LLM, it will use BambooLLM.
# You can get your free API key signing up at https://pandabi.ai (you can also configure it in your .env file)
os.environ["PANDABI_API_KEY"] = "YOUR_PANDABI_API_KEY"

agent = Agent("examples/data/Loan payments data.csv")

# Example #1: train the model with docs
agent.train(docs="Only return loans information about the past 10 years")

response = agent.chat("How many loans were paid off?")
print(response)

# Example #2: train the model with Q/A
query = "How many loans were paid off?"
code = """
import pandas as pd

df = dfs[0]
df['loan_status'].value_counts()
"""
agent.train(queries=[query], codes=[code])

response = agent.chat(query)
print(response)
