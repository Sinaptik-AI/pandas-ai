"""Example of using PandasAI with a Snowflake"""

from pandasai import SmartDataframe
from pandasai.llm import OpenAI
from pandasai.connectors import SnowFlakeConnector


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

OPEN_AI_API = "Your-API-Key"
llm = OpenAI(api_token=OPEN_AI_API)
df = SmartDataframe(snowflake_connector, config={"llm": llm})

response = df.chat("Count line status is F")
print(response)
