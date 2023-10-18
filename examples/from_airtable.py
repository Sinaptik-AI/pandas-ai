from pandasai.connectors import AirtableConnector
from pandasai.llm import OpenAI
from pandasai import SmartDataframe


airtable_connectors = AirtableConnector(
    config={
        "api_key": "AIRTABLE_API_TOKEN",
        "table": "AIRTABLE_TABLE_NAME",
        "base_id": "AIRTABLE_BASE_ID",
        "where": [
            # this is optional and filters the data to
            # reduce the size of the dataframe
            ["Status", "=", "In progress"]
        ],
    }
)

llm = OpenAI("OPENAI_API_KEY")
df = SmartDataframe(airtable_connectors, config={"llm": llm})

response = df.chat("How many rows are there in data ?")
print(response)
