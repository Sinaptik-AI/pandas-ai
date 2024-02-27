"""Example of using PandasAI with a DataBricks"""

from pandasai import Agent

# A license might be required for using Snowflake with PandasAI
from pandasai.ee.connectors import DatabricksConnector
from pandasai.llm import OpenAI

databricks_connector = DatabricksConnector(
    config={
        "host": "adb-*****.azuredatabricks.net",
        "database": "default",
        "token": "dapidfd412321",
        "port": 443,
        "table": "loan_payments_data",
        "httpPath": "/sql/1.0/warehouses/213421312",
        "where": [
            # this is optional and filters the data to
            # reduce the size of the dataframe
            ["loan_status", "=", "PAIDOFF"],
        ],
    }
)

llm = OpenAI("OPEN_API_KEY")
df = Agent([databricks_connector], config={"llm": llm})

response = df.chat("How many people from the United states?")
print(response)
