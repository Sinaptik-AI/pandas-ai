"""Example of using PandasAI with a CSV file."""

from pandasai import Agent
from pandasai.llm import OpenAI

llm = OpenAI()
df = Agent(
    ["examples/data/Loan payments data.csv"],
    config={"llm": llm, "enable_cache": False, "max_retries": 1},
)
response = df.chat("How many loans are from men and have been paid off?")
print(response)
# Output: 247 loans have been paid off by men.
