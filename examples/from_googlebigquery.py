import os
import base64
import json
from pandasai import SmartDataframe

# A license might be required for using Snowflake with PandasAI
from pandasai.ee.connectors import GoogleBigQueryConnector

# ENV's
# BIG_QUERY_DATABASE
# KEYFILE_PATH
# PROJECT_ID

# EXAMPLE 1
bigquery_connectors = GoogleBigQueryConnector(
    config={
        "credentials_path": "/Users/arslan/Downloads/loan-project.json",
        "database": "loan_payments",
        "table": "loan_payments",
        "projectID": "loan-project",
        "where": [["Gender", "=", "female"]],
    }
)

# Get your FREE API key signing up at https://pandabi.ai.
# You can also configure it in your .env file.
os.environ["PANDASAI_API_KEY"] = "your-api-key"

sdf = SmartDataframe(bigquery_connectors)

response = sdf.chat("How many rows are there in data ?")
print(response)

# EXAMPLE 2
# initialize google big query using Base64 string
with open("/Users/arslan/Downloads/loan-project.json", "r") as file:
    json_data = json.load(file)

# Convert JSON data to a string
json_string = json.dumps(json_data, indent=2)
encoded_bytes = base64.b64encode(json_string.encode("utf-8"))


bigquery_connectors = GoogleBigQueryConnector(
    config={
        "credentials_base64": encoded_bytes,
        "database": "loan_payments",
        "table": "loan_payments",
        "projectID": "loan-project",
        "where": [["Gender", "=", "female"]],
    }
)

sdf = SmartDataframe(bigquery_connectors)

response = sdf.chat("How many rows are there in data ?")
print(response)
