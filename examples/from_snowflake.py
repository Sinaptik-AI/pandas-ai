"""Example of using PandaAI with a Snowflake"""

import os

from pandasai import Agent

# The usage of this connector in production is subject to a license ([check it out](https://github.com/Sinaptik-AI/pandas-ai/blob/master/pandasai/ee/LICENSE)).
# If you plan to use it in production, [contact us](https://forms.gle/JEUqkwuTqFZjhP7h8).
from pandasai.ee.connectors import SnowflakeConnector

snowflake_connector = SnowflakeConnector(
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

# By default, unless you choose a different LLM, it will use BambooLLM.
# You can get your free API key signing up at https://pandabi.ai (you can also configure it in your .env file)
os.environ["PANDABI_API_KEY"] = "YOUR_PANDABI_API_KEY"

agent = Agent(snowflake_connector)

response = agent.chat("How many records has status 'F'?")
print(response)
