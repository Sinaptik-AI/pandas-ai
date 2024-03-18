"""Example of using PandasAI with a Snowflake"""

import os
from pandasai import Agent

# A license might be required for using Snowflake with PandasAI
from pandasai.ee.connectors import SnowFlakeConnector

snowflake_connector = SnowFlakeConnector(
    config={
        "account": "ehxzojy-ue47135",
        "database": "SNOWFLAKE_SAMPLE_DATA",
        "username": "test",
        "password": "*****",
        "table": "lineitem",
        "warehouse": "COMPUTE_WH",
        "dbSchema": "tpch_sf1",
        "where": [
            # this is optional and filters the data to
            # reduce the size of the dataframe
            ["l_quantity", ">", "49"]
        ],
    }
)

# Get your FREE API key signing up at https://pandabi.ai.
# You can also configure it in your .env file.
os.environ["PANDASAI_API_KEY"] = "your-api-key"

agent = Agent(snowflake_connector)

response = agent.chat("How many records has status 'F'?")
print(response)
