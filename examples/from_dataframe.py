"""Example of using PandaAI with a Pandas DataFrame"""

import os

import pandas as pd
from data.sample_dataframe import dataframe

from pandasai import Agent

df = pd.DataFrame(dataframe)

# By default, unless you choose a different LLM, it will use BambooLLM.
# You can get your free API key signing up at https://pandabi.ai (you can also configure it in your .env file)
os.environ["PANDABI_API_KEY"] = "YOUR_PANDABI_API_KEY"

agent = Agent(dataframe)
response = agent.chat("Calculate the sum of the gdp of north american countries")
print(response)
# Output: 20901884461056
