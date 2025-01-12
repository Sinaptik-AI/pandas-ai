"""Example of using PandaAI with a CSV file."""

import os

from pandasai import Agent
from pandasai.connectors import MySQLConnector, PostgreSQLConnector, SqliteConnector

# With a MySQL database
loan_connector = MySQLConnector(
    config={
        "host": "localhost",
        "port": 3306,
        "database": "mydb",
        "username": "root",
        "password": "root",
        "table": "loans",
        "where": [
            # this is optional and filters the data to
            # reduce the size of the dataframe
            ["loan_status", "=", "PAIDOFF"],
        ],
    }
)

# With a PostgreSQL database
payment_connector = PostgreSQLConnector(
    config={
        "host": "localhost",
        "port": 5432,
        "database": "mydb",
        "username": "root",
        "password": "root",
        "table": "payments",
        "where": [
            # this is optional and filters the data to
            # reduce the size of the dataframe
            ["payment_status", "=", "PAIDOFF"],
        ],
    }
)

# With a Sqlite database

invoice_connector = SqliteConnector(
    config={
        "database": "local_path_to_db",
        "table": "invoices",
        "where": [["status", "=", "pending"]],
    }
)

# By default, unless you choose a different LLM, it will use BambooLLM.
# You can get your free API key signing up at https://pandabi.ai (you can also configure it in your .env file)
os.environ["PANDASAI_API_KEY"] = "your-api-key"

agent = Agent([loan_connector, payment_connector, invoice_connector])
response = agent.chat("How many people from the United states?")
print(response)
# Output: 247 loans have been paid off by men.
