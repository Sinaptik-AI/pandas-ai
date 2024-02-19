"""Example of using PandasAI with a CSV file."""

from pandasai import Agent
from pandasai.llm import OpenAI
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
llm = OpenAI()
df = Agent([loan_connector, payment_connector, invoice_connector], config={"llm": llm})
response = df.chat("How many people from the United states?")
print(response)
# Output: 247 loans have been paid off by men.
