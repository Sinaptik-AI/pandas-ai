"""Example of using PandaAI with a DataBricks"""

import os

from pandasai import Agent

# The usage of this connector in production is subject to a license ([check it out](https://github.com/Sinaptik-AI/pandas-ai/blob/master/pandasai/ee/LICENSE)).
# If you plan to use it in production, [contact us](https://forms.gle/JEUqkwuTqFZjhP7h8).
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

# By default, unless you choose a different LLM, it will use BambooLLM.
# You can get your free API key signing up at https://pandabi.ai (you can also configure it in your .env file)
os.environ["PANDASAI_API_KEY"] = "your-api-key"

agent = Agent(databricks_connector)

response = agent.chat("How many people from the United states?")
print(response)
