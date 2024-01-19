"""Example of using PandasAI with a CSV file."""

from pandasai import SmartDatalake
from pandasai.llm import OpenAI
from pandasai.connectors import PostgreSQLConnector
from pandasai.smart_dataframe import Agent


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


llm = OpenAI("OPEN_API_KEY")


order_details_smart_df = Agent(
    [order_details],
    config={"llm": llm, "direct_sql": True},
    description="Contain user order details",
)


df = SmartDatalake(
    [order_details_smart_df, order, products],
    config={"llm": llm, "direct_sql": True},
)
response = df.chat("return orders with count of distinct products")
print(response)
