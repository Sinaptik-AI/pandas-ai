from pandasai import SmartDataframe
from pandasai.connectors.yahoo_finance import YahooFinanceConnector
from pandasai.llm import OpenAI

yahoo_connector = YahooFinanceConnector("MSFT")

llm = OpenAI(api_token="OPEN_API_KEY")
df = SmartDataframe(yahoo_connector, config={"llm": llm})

response = df.chat("What is the closing price for yesterday?")
print(response)
