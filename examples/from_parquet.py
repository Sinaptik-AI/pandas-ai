"""Example of using PandasAI with a Parquet file."""

import pandas as pd
from pandasai import SmartDataframe
from pandasai.llm import OpenAI

parquet_file_path = "examples/data/Loan payments data.parquet"
df = pd.read_parquet(parquet_file_path)

llm = OpenAI()

smart_df_read = SmartDataframe(df=df, config={"llm": llm})
response = smart_df_read.chat("How many loans are from men and have been paid off?")
print(response)
# Output: 247 loans have been paid off by men.













