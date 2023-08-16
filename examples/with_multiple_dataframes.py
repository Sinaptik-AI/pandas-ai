"""Example of using PandasAI on multiple Pandas DataFrame"""

import pandas as pd

from pandasai import SmartDatalake
from pandasai.llm import OpenAI

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

llm = OpenAI()
dl = SmartDatalake(
    [employees_df, salaries_df],
    config={
        "llm": llm,
        "verbose": True,
    },
)
response = dl.chat("Who gets paid the most?")
print(response)
# Output: Olivia
