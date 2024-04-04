"""Example of using PandasAI with a Pandas DataFrame"""
import os

import pandas as pd

from pandasai import Agent

from .data.sample_dataframe import dataframe

# By default, unless you choose a different LLM, it will use BambooLLM.
# You can get your free API key signing up at https://pandabi.ai (you can also configure it in your .env file)
os.environ["PANDASAI_API_KEY"] = "YOUR_API_KEY"

agent = Agent([pd.DataFrame(dataframe)], config={"enforce_privacy": True})
response = agent.chat("Calculate the sum of the gdp of north american countries")
print(response)
# Output: 20901884461056
