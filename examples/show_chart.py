"""Example of using PandasAI to generate a chart from a Pandas DataFrame"""

import os
import pandas as pd
from data.sample_dataframe import dataframe
from pandasai import Agent

df = pd.DataFrame(dataframe)

# Get your FREE API key signing up at https://pandabi.ai.
# You can also configure it in your .env file.
os.environ["PANDASAI_API_KEY"] = "your-api-key"

agent = Agent(df)
response = agent.chat(
    "Plot the histogram of countries showing for each the gpd,"
    " using different colors for each bar",
)
# Output: check out images/histogram-chart.png
