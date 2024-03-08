import os

from pandasai import Agent

# Set your PandasAI API key (you can generate one signing up at https://pandabi.ai)
os.environ["PANDASAI_API_KEY"] = "YOUR_PANDASAI_API_KEY"

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
