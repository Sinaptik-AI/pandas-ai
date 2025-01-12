import os

from extensions.connectors.yfinance.pandasai_yfinance.yahoo_finance import (
    YahooFinanceConnector,
)
from pandasai import Agent

yahoo_connector = YahooFinanceConnector("MSFT")

# By default, unless you choose a different LLM, it will use BambooLLM.
# You can get your free API key signing up at https://pandabi.ai (you can also configure it in your .env file)
os.environ["PANDABI_API_KEY"] = "YOUR_PANDABI_API_KEY"

agent = Agent(yahoo_connector)

response = agent.chat("What is the closing price for yesterday?")
print(response)
