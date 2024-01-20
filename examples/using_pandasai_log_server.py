import os

import pandas as pd

from pandasai import Agent
from pandasai.llm.openai import OpenAI

employees_data = {
    "EmployeeID": [1, 2, 3, 4, 5],
    "Name": ["John", "Emma", "Liam", "Olivia", "William"],
    "Department": ["HR", "Sales", "IT", "Marketing", "Finance"],
}

salaries_data = {
    "EmployeeID": [1, 2, 3, 4, 5],
    "Salary": [5000, 6000, 4500, 7000, 5500],
}

employees_df = pd.DataFrame(employees_data)
salaries_df = pd.DataFrame(salaries_data)

# Example 1: Using Environment Variables
os.environ["LOGGING_SERVER_URL"] = "SERVER_URL"
os.environ["LOGGING_SERVER_API_KEY"] = "YOUR_API_KEY"


llm = OpenAI("YOUR_API_KEY")
agent = Agent(
    [employees_df, salaries_df],
    config={
        "llm": llm,
        "enable_cache": True,
    },
    memory_size=10,
)

# Chat with the agent
response = agent.chat("Plot salary against department?")
print(response)


# Example 2: Using Config
llm = OpenAI("YOUR_API_KEY")
agent = Agent(
    [employees_df, salaries_df],
    config={
        "llm": llm,
        "enable_cache": True,
        "log_server": {
            "server_url": "SERVER_URL",
            "api_key": "YOUR_API_KEY",
        },
    },
    memory_size=10,
)

# Chat with the agent
response = agent.chat("Plot salary against department?")

print(response)
