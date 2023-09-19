from pandasai.connectors.yahoo_finance import YahooFinanceConnector
from pandasai import SmartDataframe
from pandasai.llm import OpenAI


yahoo_connector = YahooFinanceConnector("MSFT")


OPEN_AI_API = "OPEN_API_KEY"
llm = OpenAI(api_token=OPEN_AI_API)
df = SmartDataframe(yahoo_connector, config={"llm": llm})

response = df.chat("closing price yesterday")
print(response)
