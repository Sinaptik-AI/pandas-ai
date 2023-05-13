import os

import pandas as pd
from dotenv import load_dotenv

from pandasai import PandasAI
from pandasai.llm.openai import OpenAI

load_dotenv()
# get sheet id from url

sheet_id = os.getenv("Google_Sheets")
sheet_name = "second"
r""" if getting an SSl error and on macOS, run the following command in 
terminal: /Applications/Python\ 3.11/Install\ Certificates.command """


def sheets_input(sheet_id, sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    return pd.read_csv(url)


llm = OpenAI()
pandas_ai = PandasAI(llm, verbose=True, conversational=False)
# google sheets id should look something like this: 1IRGJRUpCR0-9tPDd2MgPjQCtNft_4a8B1fHbYK7_LM8
# second input is google sheets n
response = pandas_ai.run(
    sheets_input(os.getenv("Google_Sheets"), "second"),
    "Calculate the sum of the gdp of north american countries",
)
print(response)
# Output: 20901884461056
