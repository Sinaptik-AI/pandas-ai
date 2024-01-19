"""Example of using PandasAI with a CSV file and Google Vertexai."""

import os
import pandas as pd
from pandasai import Agent
from pandasai.llm import GoogleVertexAI

df = pd.read_csv("examples/data/Loan payments data.csv")

# Set the path of your json credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "application_default_credentials.json"

llm = GoogleVertexAI(
    project_id="generative-ai-training", location="us-central1", model="text-bison@001"
)
df = Agent([df], config={"llm": llm})
response = df.chat("How many loans are from men and have been paid off?")
print(response)
# Output: 247 loans have been paid off by men.
