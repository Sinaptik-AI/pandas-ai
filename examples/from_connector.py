"""Example of using PandasAI with a connector."""

from pandasai import SmartDataframe
from pandasai.llm import OpenAI
from pandasai.connectors import MySQLConnector

llm = OpenAI()
connector = MySQLConnector(
    {
        "host": "localhost",
        "user": "root",
        "password": "root",
        "database": "database",
        "table": "users",
    }
)

df = SmartDataframe(connector, config={"llm": llm})
response = df.chat("How many users subscribed in the last 24 hours?")
print(response)
# Output: 115 users subscribed in the last 24 hours.
