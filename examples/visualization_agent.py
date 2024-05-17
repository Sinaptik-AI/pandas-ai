import os

from pandasai.connectors.sql import PostgreSQLConnector
from pandasai.ee.agents.visualization_agent import VisualizationAgent

config_ = {"enable_cache": False, "direct_sql": True}

payment_connector = PostgreSQLConnector(
    config={
        "host": "testdb.*******",
        "port": 5432,
        "database": "testdb",
        "username": "postgres",
        "password": "*******",
        "table": "orders",
        "connect_args": {"sslmode": "require", "sslrootcert": None},
    },
    field_descriptions={"customer_id": "foreign key"},
)

os.environ["PANDASAI_API_KEY"] = "$2a$10$HonhhCCzvE***********************"


agent = VisualizationAgent([payment_connector], config=config_, memory_size=10)

# Chat with the agent
response = agent.chat("return orders count groupby country")

print(agent.last_code_generated)
print(agent.last_code_executed)
