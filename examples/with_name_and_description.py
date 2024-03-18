"""Example of using PandasAI with a Pandas DataFrame"""

import pandas as pd
from data.sample_dataframe import dataframe
from pandasai import Agent
import os

df = pd.DataFrame(dataframe)

# Get your FREE API key signing up at https://pandabi.ai.
# You can also configure it in your .env file.
os.environ["PANDASAI_API_KEY"] = "YOUR_API_KEY"

agent = Agent(
    dataframe,
    name="Countries",
    description="A dataframe with countries with their GDPs and happiness scores",
)
response = agent.chat("Calculate the sum of the gdp of north american countries")
print(response)
print(df.last_prompt)
# Output: 20901884461056
