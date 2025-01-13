from pandasai_openai import OpenAI
from pandasai_sql.sql import PostgreSQLConnector

from pandasai.agent.base import Agent
from pandasai.ee.connectors.relations import ForeignKey, PrimaryKey

llm = OpenAI("sk-*************")

config_ = {"llm": llm}

payment_connector = PostgreSQLConnector(
    config={
        "host": "localhost",
        "port": 5432,
        "database": "testdb",
        "username": "postgres",
        "password": "*****",
        "table": "orders",
    },
    connector_relations=[
        PrimaryKey("id"),
        ForeignKey(
            field="customer_id", foreign_table="customers", foreign_table_field="id"
        ),
    ],
)

customer_connector = PostgreSQLConnector(
    config={
        "host": "localhost",
        "port": 5432,
        "database": "mydb",
        "username": "root",
        "password": "root",
        "table": "customers",
    },
    connector_relations=[PrimaryKey("id")],
)

agent = Agent([payment_connector, customer_connector], config=config_, memory_size=10)

response = agent.chat("return orders count groupby country")

print(response)
