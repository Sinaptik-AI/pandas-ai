"""Example of using PandasAI with a Snowflake"""

from pandasai import SmartDataframe
from pandasai.llm import OpenAI
from pandasai.connectors import DatabricksConnector

databricks_connector = DatabricksConnector(
    config={
        "host": "ehxzojy-ue47135",
        "database": "SNOWFLAKE_SAMPLE_DATA",
        "token": "",
        "port": 443,
        "table": "lineitem",
        "httpPath": "tpch_sf1",
        "where": [
            # this is optional and filters the data to
            # reduce the size of the dataframe
            ["l_quantity", ">", "49"]
        ],
    }
)

llm = OpenAI(api_token="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")
df = SmartDataframe(databricks_connector, config={"llm": llm})

response = df.chat("How many records has status 'F'?")
print(response)
