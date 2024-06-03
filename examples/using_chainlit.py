"""
Example of using Chainlit to chat with PandasAI data frames
Chainlit is an open-source Python package to build production ready Conversational AI.
https://docs.chainlit.io

Usage:
chainlit run examples/using_chainlit.py
"""

import os

import pandas as pd

from pandasai import SmartDataframe

import chainlit as cl

# Sample DataFrame
sales_by_country = pd.DataFrame({
    "country": ["United States", "United Kingdom", "France", "Germany", "Italy", "Spain", "Canada", "Australia", "Japan", "China"],
    "sales": [5000, 3200, 2900, 4100, 2300, 2100, 2500, 2600, 4500, 7000]
})


# By default, unless you choose a different LLM, it will use BambooLLM.
# You can get your free API key signing up at https://pandabi.ai (you can also configure it in your .env file)
os.environ["PANDASAI_API_KEY"] = "your-api-key"

# Create a PandasAI SmartDataframe from pandas DataFrame
df = SmartDataframe(sales_by_country)

# This function is called for each chat/reponse cycle
@cl.on_message
async def on_message(message: cl.Message):

    # send empty content response to display a loader animation
    msg = cl.Message(content="")
    await msg.send()


    # Example: 
    # User Question: Which are the top 5 countries by sales?
    # LLM Response: China, United States, Japan, Germany, Australia


    # what did the user type for a question?
    user_question = message.content

    # feed the llm the question and get the response
    llm_response = df.chat(user_question)


    # load the response into chainlit
    msg.content=llm_response
    
    # send the response
    await msg.update()

    