"""Example of using PandasAI with a Snowflake"""

from pandasai import Agent

# A license might be required for using Snowflake with PandasAI
from pandasai.ee.connectors import SnowFlakeConnector

from pandasai.llm import OpenAI

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

llm = OpenAI(api_token="OPEN_API_KEY")
df = Agent([snowflake_connector], config={"llm": llm})

response = df.chat("How many records has status 'F'?")
print(response)
