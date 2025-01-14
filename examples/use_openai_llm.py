import pandasai as pai
from pandasai_openai import OpenAI

llm = OpenAI(api_token="your_api_token")

pai.config.set({
    "llm": llm,
})

df = pai.read_csv("./datasets/heart.csv")

response = df.chat("What is the correlation between age and cholesterol?")