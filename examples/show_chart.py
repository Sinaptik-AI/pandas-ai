"""Example of using PandaAI to generate a chart from a Pandas DataFrame"""

import os

import pandas as pd
from data.sample_dataframe import dataframe

from pandasai import Agent

df = pd.DataFrame(dataframe)

# By default, unless you choose a different LLM, it will use BambooLLM.
# You can get your free API key signing up at https://pandabi.ai (you can also configure it in your .env file)
os.environ["PANDABI_API_KEY"] = "YOUR_PANDABI_API_KEY"

agent = Agent(df)
response = agent.chat(
    "Plot the histogram of countries showing for each the gpd,"
    " using different colors for each bar",
)
# Output: check out assets/histogram-chart.png
