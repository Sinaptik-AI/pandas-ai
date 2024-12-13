import os
import pandasai as pai
from pandasai_openai import OpenAI

os.environ["PANDASAI_API_URL"] = "http://localhost:8000/"
os.environ["PANDASAI_API_KEY"] = "PAI-test-key"

llm = OpenAI(api_token="your-key")
# Print LLM details
print("LLM Type:", type(llm).__name__)
print("LLM Instance:", llm)
print("LLM Model:", llm.model)

pai.config.set({
   "llm": llm,
})

# Print current config to verify LLM setting
print("\nCurrent PandasAI Config:")
print("Active LLM:", pai.config._config.llm)

df = pai.load("/home/giuseppe/Projects/pandas-ai/datasets/testing/loans")
print(df.head())

response = df.chat("What is the average age of the borrowers?")

print(response)