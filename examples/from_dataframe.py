"""Example of using PandasAI with a Pandas DataFrame"""

import os

import pandas as pd
from data.sample_dataframe import dataframe

from pandasai import Agent

df = pd.DataFrame(dataframe)

# Get your FREE API key signing up at https://pandabi.ai.
# You can also configure it in your .env file.
os.environ["PANDASAI_API_KEY"] = "your-api-key"

agent = Agent(dataframe)
response = agent.chat("Calculate the sum of the gdp of north american countries")
print(response)
# Output: 20901884461056
