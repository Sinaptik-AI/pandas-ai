"""Example of using PandasAI to generate and save a chart from a Pandas DataFrame"""

import os

import pandas as pd
from data.sample_dataframe import dataframe

from pandasai import Agent
from pandasai.helpers import path

df = pd.DataFrame(dataframe)

try:
    user_defined_path = path.find_project_root()
except ValueError:
    user_defined_path = os.getcwd()

# By default, unless you choose a different LLM, it will use BambooLLM.
# You can get your free API key signing up at https://pandabi.ai (you can also configure it in your .env file)
os.environ["PANDABI_API_KEY"] = "YOUR_PANDABI_API_KEY"

user_defined_path = os.path.join(user_defined_path, "exports", "charts")
agent = Agent(
    df,
    config={
        "save_charts_path": user_defined_path,
        "save_charts": True,
        "verbose": True,
    },
)
response = agent.chat(
    "Plot the histogram of countries showing for each the gpd,"
    " using different colors for each bar",
)
# Output: check out $pwd/exports/charts/{hashid}/chart.png
