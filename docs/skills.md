# Skills

You can add customs functions for the agent to use, allowing the agent to expand its capabilities. These custom functions can be seamlessly integrated with the agent's skills, enabling a wide range of user-defined operations.

## Example Usage

```python

import pandas as pd
from pandasai import Agent

from pandasai.llm.openai import OpenAI
from pandasai.skills import skill

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


@skill(
    name="Display employee salary",
    description="Plots the employee salaries against names",
    usage="Displays the plot having name on x axis and salaries on y axis",
)
def plot_salaries(name: list[str], salary: list[int]) -> str:
    import matplotlib.pyplot as plt

    plt.bar(name, salary)
    plt.xlabel("Employee Name")
    plt.ylabel("Salary")
    plt.title("Employee Salaries")
    plt.xticks(rotation=45)
    plt.savefig("temp_chart.png")
    plt.close()



llm = OpenAI("YOUR_API_KEY")
agent = Agent([employees_df, salaries_df], config={"llm": llm}, memory_size=10)

agent.add_skills(plot_salaries)

# Chat with the agent
response = agent.chat("Plot the employee salaries against names")


```

## Add Streamlit Skill

```python
import pandas as pd
from pandasai import Agent

from pandasai.llm.openai import OpenAI
from pandasai.skills import skill
import streamlit as st

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


@skill(
    name="Display employee salary",
    description="Plots the employee salaries against names",
    usage="Displays the plot having name on x axis and salaries on y axis",
)
def plot_salaries(name: list[str], salary: list[int]) -> str:
    import matplotlib.pyplot as plt

    plt.bar(name, salary)
    plt.xlabel("Employee Name")
    plt.ylabel("Salary")
    plt.title("Employee Salaries")
    plt.xticks(rotation=45)
    plt.savefig("temp_chart.png")
    fig = plt.gcf()
    st.pyplot(fig)


llm = OpenAI("YOUR_API_KEY")
agent = Agent([employees_df, salaries_df], config={"llm": llm}, memory_size=10)

agent.add_skills(plot_salaries_using_streamlit)

# Chat with the agent
response = agent.chat("Plot the employee salaries against names")
print(response)
```
