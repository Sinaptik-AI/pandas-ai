"""Example of using PandasAI on multiple Pandas DataFrame"""

import pandas as pd
from pandasai import Agent
import os

employees_df = pd.DataFrame(
    {
        "EmployeeID": [1, 2, 3, 4, 5],
        "Name": ["John", "Emma", "Liam", "Olivia", "William"],
        "Department": ["HR", "Sales", "IT", "Marketing", "Finance"],
    }
)

salaries_df = pd.DataFrame(
    {
        "EmployeeID": [1, 2, 3, 4, 5],
        "Salary": [5000, 6000, 4500, 7000, 5500],
    }
)

# Get your FREE API key signing up at https://pandabi.ai.
# You can also configure it in your .env file.
os.environ["PANDASAI_API_KEY"] = "YOUR_API_KEY"

agent = Agent([employees_df, salaries_df])
response = agent.chat("Plot salaries against name")
print(response)
# Output: <displays the plot>
