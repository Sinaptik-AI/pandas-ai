# """Example of using PandasAI with a CSV file."""

# from pandasai import Agent

# # By default, unless you choose a different LLM, it will use BambooLLM.
# # You can get your free API key signing up at https://pandabi.ai (you can also configure it in your .env file)

# agent = Agent(
#     "examples/data/Loan payments data.csv",
# )
# response = agent.chat("How many loans are from men and have been paid off?")

# print(response)
# # Output: 247 loans have been paid off by men.


import pandasai as pai
import pandasai_sql

df = pai.load("sipa/users")
response = df.chat("How many users in total?")
print(response)