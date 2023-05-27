"""Example of using PandasAI with a Google Sheets file."""

import pandas as pd

from pandasai import PandasAI
from pandasai.helpers.datasource import sheets_input
from pandasai.llm.openai import OpenAI

# instructions:
# https://docs.google.com/document/d/1uAmXI3e8Wm26lZQb0bYIJaXRdZi5WLJKNJHT59QMGEc/edit?usp=sharing
df = sheets_input(
    "1IRGJFUpCR0-9tPDk2MgPjQCtNft_4a8B1fHgYK7_LM8",
    "second",
    "../service_account_file.json",
)
# specify type of columns, google sheets is not strongly typed
df["gdp"] = pd.to_numeric(df["gdp"])
df["happiness_index"] = pd.to_numeric(df["happiness_index"])

llm = OpenAI()
pandas_ai = PandasAI(llm, verbose=True, conversational=False)

response = pandas_ai.run(
    df,
    "Calculate the sum of the gdp of north american countries",
)
print(response)
Output: 20901884461056
