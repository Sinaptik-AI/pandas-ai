"""Example of using PandasAI with a Parquet file."""

from pandasai import SmartDataframe
from pandasai.llm import OpenAI

llm = OpenAI()

smart_df_read = SmartDataframe(df="examples/data/Loan payments data.parquet", config={"llm": llm})
response = smart_df_read.chat("How many loans are from men and have been paid off?")
print(response)
# Output: 247 loans have been paid off by men.













