"""Example of using PandasAI with a CSV file and Google Vertexai."""

import pandas as pd

from pandasai import PandasAI
from pandasai.llm.google_palm import GoogleVertexai

df = pd.read_csv("examples/data/Loan payments data.csv")

llm = GoogleVertexai(project_id="generative-ai-training",
                     location="us-central1",
                     model="text-bison@001")
pandas_ai = PandasAI(llm, verbose=True, conversational=True)
response = pandas_ai.run(df, "How many loans are from men and have been paid off?")
print(response)
# Output: 247 loans have been paid off by men.
