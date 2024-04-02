import os

from pandasai import Agent

# Get your FREE API key signing up at https://pandabi.ai.
# You can also configure it in your .env file.
os.environ["PANDASAI_API_KEY"] = "YOUR_API_KEY"

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
