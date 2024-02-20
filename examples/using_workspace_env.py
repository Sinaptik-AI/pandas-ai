import os

import pandas as pd

from pandasai import Agent
from pandasai.llm.openai import OpenAI
from pandasai.schemas.df_config import Config

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


os.environ["PANDASAI_WORKSPACE"] = "workspace dir path"


llm = OpenAI("YOUR_API_KEY")
config__ = {"llm": llm, "save_charts": False}


agent = Agent(
    [employees_df, salaries_df],
    config=Config(**config__),
    memory_size=10,
)

# Chat with the agent
response = agent.chat("plot salary against department?")
print(response)
