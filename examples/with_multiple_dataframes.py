"""Example of using PandasAI on multiple Pandas DataFrame"""

import pandas as pd
from pandasai import PandasAI
from pandasai.llm.openai import OpenAI

employees_data = {
    'EmployeeID': [1, 2, 3, 4, 5],
    'Name': ['John', 'Emma', 'Liam', 'Olivia', 'William'],
    'Department': ['HR', 'Sales', 'IT', 'Marketing', 'Finance']
}

salaries_data = {
    'EmployeeID': [1, 2, 3, 4, 5],
    'Salary': [5000, 6000, 4500, 7000, 5500]
}

employees_df = pd.DataFrame(employees_data)
salaries_df = pd.DataFrame(salaries_data)


llm = OpenAI()
pandas_ai = PandasAI(llm, verbose=True)
response = pandas_ai([employees_df, salaries_df], "Who gets paid the most?")
print(response)
# Output: Olivia
