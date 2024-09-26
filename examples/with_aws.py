"""Example of using PandasAI with a Dataframe and Amazon Bedrock."""

import pandas as pd
from pandasai import Agent
from pandasai.llm import BedrockClaude
import boto3

# Configure the AWS account credential files : https://docs.aws.amazon.com/cli/v1/userguide/cli-configure-files.html

region = "us-east-1"
bedrock_runtime_client = boto3.client("bedrock-runtime", region_name=region)

df = pd.DataFrame(
    {
        "country": [
            "United States",
            "United Kingdom",
            "France",
            "Germany",
            "Italy",
            "Spain",
            "Canada",
            "Australia",
            "Japan",
            "China",
        ],
        "sales": [5000, 3200, 2900, 4100, 2300, 2100, 2500, 2600, 4500, 7000],
    }
)

# To check supported models : https://github.com/dimwael/pandas-ai/blob/main/pandasai/llm/bedrock_claude.py
model_id = "anthropic.claude-3-haiku-20240307-v1:0"

llm = BedrockClaude(model=model_id, bedrock_runtime_client=bedrock_runtime_client)

agent = Agent(df, config={"llm": llm})
response = agent.chat("What is the sum of sales for Us and UK ")
print(response)
# 8200
