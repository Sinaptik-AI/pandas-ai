"""Example of using PandasAI with a CSV file."""

from pandasai import SmartDataframe
from pandasai.llm import OpenAI
from pandasai.connectors import MySQLConnector, PostgreSQLConnector

# With a MySQL database
connector = MySQLConnector(
    config={
        "host": "localhost",
        "port": 3306,
        "database": "mydb",
        "username": "root",
        "password": "root",
        "table": "loans",
        "where": {
            # this is optional and filters the data to
            # reduce the size of the dataframe
            "loan_status": "PAIDOFF",
        },
    }
)
df = connector.execute()

# With a PostgreSQL database
connector = PostgreSQLConnector(
    config={
        "host": "localhost",
        "port": 5432,
        "database": "mydb",
        "username": "root",
        "password": "root",
        "table": "loans",
        "where": {
            # this is optional and filters the data to
            # reduce the size of the dataframe
            "loan_status": "PAIDOFF",
        },
    }
)
df = connector.execute()

llm = OpenAI()
df = SmartDataframe(df, config={"llm": llm})
response = df.chat("How many people from the United states?")
print(response)
# Output: 247 loans have been paid off by men.
