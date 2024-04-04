import os

from pandasai import Agent
from pandasai.connectors import AirtableConnector

airtable_connectors = AirtableConnector(
    config={
        "token": "AIRTABLE_API_TOKEN",
        "table": "AIRTABLE_TABLE_NAME",
        "base_id": "AIRTABLE_BASE_ID",
        "where": [
            # this is optional and filters the data to
            # reduce the size of the dataframe
            ["Status", "=", "In progress"]
        ],
    }
)

# By default, unless you choose a different LLM, it will use BambooLLM.
# You can get your free API key signing up at https://pandabi.ai (you can also configure it in your .env file)
os.environ["PANDASAI_API_KEY"] = "your-api-key"

agent = Agent(airtable_connectors)

response = agent.chat("How many rows are there in data ?")
print(response)
