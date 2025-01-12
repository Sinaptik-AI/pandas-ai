import base64
import json
import os

from pandasai import SmartDataframe

# The usage of this connector in production is subject to a license ([check it out](https://github.com/Sinaptik-AI/pandas-ai/blob/master/pandasai/ee/LICENSE)).
# If you plan to use it in production, [contact us](https://forms.gle/JEUqkwuTqFZjhP7h8).
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

# By default, unless you choose a different LLM, it will use BambooLLM.
# You can get your free API key signing up at https://pandabi.ai (you can also configure it in your .env file)
os.environ["PANDABI_API_KEY"] = "YOUR_PANDABI_API_KEY"

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
