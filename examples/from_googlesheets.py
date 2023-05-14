import os

import pandas as pd
from dotenv import load_dotenv

from pandasai import PandasAI
from pandasai.helpers.datasource import sheets_input
from pandasai.llm.openai import OpenAI

load_dotenv()

# google sheets id should look something like this: 1IRGJRUpCR0-9tPDd2MgPjQCtNft_4a8B1fHbYK7_LM8
# second input is google sheet name
sheet_id = os.getenv("Google_Sheets")
sheet_name = "second"

r""" if getting an SSl error and on macOS, run the following command in 
terminal: /Applications/Python\ 3.11/Install\ Certificates.command """


df = sheets_input(sheet_id, sheet_name)


llm = OpenAI()
pandas_ai = PandasAI(llm, verbose=True, conversational=False)

response = pandas_ai.run(
    df,
    "Calculate the sum of the gdp of north american countries",
)
print(response)
# Output: 20901884461056
