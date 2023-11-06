"""Example of using PandasAI with a CSV file."""

from pandasai import SmartDatalake
from pandasai.llm import OpenAI
from pandasai.connectors import PostgreSQLConnector


# With a PostgreSQL database
payment_connector = PostgreSQLConnector(
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


llm = OpenAI("YOUR_API_KEY")
df = SmartDatalake(
    [order_details, payment_connector, products],
    config={"llm": llm, "direct_sql": True},
)
response = df.chat("Return Orders with OrderDetails and counts of distinct Products")
print(response)
