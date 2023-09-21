import pandas as pd
from pandasai.agent import Agent

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


llm = OpenAI("OPEN_API")
dl = Agent([employees_df, salaries_df], config={"llm": llm}, memory_size=10)
response = dl.chat("Who gets paid the most?")
print(response)
response = dl.clarification_questions()

response = dl.chat("Which department does he belongs to?")
print(response)
