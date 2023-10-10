import pandas as pd
from pandasai import Agent
from pandasai.custom_loggers.api_logger import APILogger

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


llm = OpenAI("Your-API-Key")
agent = Agent(
    [employees_df, salaries_df],
    config={"llm": llm, "enable_cache": True},
    memory_size=10,
    logger=APILogger("SERVER-URL", "USER-ID", "API-KEY"),
)

# Chat with the agent
response = agent.chat("Who gets paid the most?")
print(response)
