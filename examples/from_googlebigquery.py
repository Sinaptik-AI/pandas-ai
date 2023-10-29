from pandasai.connectors import GoogleBigQueryConnector
from pandasai.llm import OpenAI
from pandasai import SmartDataframe


bigquery_connectors = GoogleBigQueryConnector(
    config={
        "credentials_path" : "path to keyfile.json",
        "database" : "dataset_name",
        "table" : "table_name",
        "projectID" : "Project_id_name",
        "where": [
            # this is optional and filters the data to
            # reduce the size of the dataframe
            ["Status", "=", "In progress"]
        ],
    }
)

llm = OpenAI("OPENAI_API_KEY")
df = SmartDataframe(bigquery_connectors, config={"llm": llm})

response = df.chat("How many rows are there in data ?")
print(response)
