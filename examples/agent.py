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


llm = OpenAI("sk-lyDyNVyBwnykr1lJ4Yc7T3BlbkFJtJNyJlKTAvUa2E2D5Wdb44")
agent = Agent([employees_df, salaries_df], config={"llm": llm}, memory_size=10)

# Chat with the agent
response = agent.chat("Who gets paid the most?")
print(response)


# Get Clarification Questions
response = agent.clarification_questions()

if response:
    for question in response.questions:
        print(question)
else:
    print(response.message)


# Explain how the chat response is generated
response = agent.explain()
print(response)
