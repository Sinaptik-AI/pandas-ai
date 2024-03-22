"""Example of using PandasAI with a DataBricks"""

import os

from pandasai import Agent

# A license might be required for using Snowflake with PandasAI
from pandasai.ee.connectors import DatabricksConnector

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

# Get your FREE API key signing up at https://pandabi.ai.
# You can also configure it in your .env file.
os.environ["PANDASAI_API_KEY"] = "your-api-key"

agent = Agent(databricks_connector)

response = agent.chat("How many people from the United states?")
print(response)
