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

# Function doc string to give more context to the model for use this skill
@skill
def plot_salaries(names: list[str], salaries: list[int]):
    """
    Displays the bar chart  having name on x-axis and salaries on y-axis
    Args:
        names (list[str]): Employees' names
        salaries (list[int]): Salaries
    """
    # plot bars
    import matplotlib.pyplot as plt

    plt.bar(names, salaries)
    plt.xlabel("Employee Name")
    plt.ylabel("Salary")
    plt.title("Employee Salaries")
    plt.xticks(rotation=45)



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

# Function doc string to give more context to the model for use this skill
@skill
def plot_salaries(names: list[str], salaries: list[int]):
    """
    Displays the bar chart having name on x-axis and salaries on y-axis using streamlit
    Args:
        names (list[str]): Employees' names
        salaries (list[int]): Salaries
    """
    import matplotlib.pyplot as plt

    plt.bar(names, salaries)
    plt.xlabel("Employee Name")
    plt.ylabel("Salary")
    plt.title("Employee Salaries")
    plt.xticks(rotation=45)
    plt.savefig("temp_chart.png")
    fig = plt.gcf()
    st.pyplot(fig)


llm = OpenAI("YOUR_API_KEY")
agent = Agent([employees_df, salaries_df], config={"llm": llm}, memory_size=10)

agent.add_skills(plot_salaries)

# Chat with the agent
response = agent.chat("Plot the employee salaries against names")
print(response)
```
