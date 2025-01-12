"""Example of using PandaAI with a Pandas DataFrame"""

import pandas as pd
from data.sample_dataframe import dataframe

from pandasai import Agent
from pandasai.llm import AzureOpenAI

df = pd.DataFrame(dataframe)

# export AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
# export AZURE_OPENAI_API_KEY=<your Azure OpenAI API key>

# The name of your deployed model
# This will correspond to the custom name you chose for your
# deployment when you deployed a model.
deployment_name = "YOUR-MODEL-DEPLOYMENT-NAME"

llm = AzureOpenAI(
    deployment_name=deployment_name,
    api_version="2023-05-15",
    # is_chat_model=False,  # Comment in if you deployed a completion model
)

agent = Agent(df, config={"llm": llm})
response = agent.chat("Calculate the sum of the gdp of north american countries")
print(response)
# Output: 20901884461056
