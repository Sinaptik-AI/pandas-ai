"""Example of using PandasAI with a CSV file."""
import os
from pandasai import Agent
from pandasai.connectors import PostgreSQLConnector

# With a PostgreSQL database
order = PostgreSQLConnector(
    config={
        "host": "localhost",
        "port": 5432,
        "database": "testdb",
        "username": "postgres",
        "password": "123456",
        "table": "orders",
    }
)

order_details = PostgreSQLConnector(
    config={
        "host": "localhost",
        "port": 5432,
        "database": "testdb",
        "username": "postgres",
        "password": "123456",
        "table": "order_details",
    }
)

products = PostgreSQLConnector(
    config={
        "host": "localhost",
        "port": 5432,
        "database": "testdb",
        "username": "postgres",
        "password": "123456",
        "table": "products",
    }
)

# Get your FREE API key signing up at https://pandabi.ai.
# You can also configure it in your .env file.
os.environ["PANDASAI_API_KEY"] = "your-api-key"

agent = Agent(
    [order, products, order_details],
    config={"direct_sql": True},
)

response = agent.chat("return orders with count of distinct products")
print(response)
