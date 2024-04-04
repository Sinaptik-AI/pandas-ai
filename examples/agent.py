import os

import pandas as pd

from pandasai import Agent

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

# By default, unless you choose a different LLM, it will use BambooLLM.
# You can get your free API key signing up at https://pandabi.ai (you can also configure it in your .env file)
os.environ["PANDASAI_API_KEY"] = "your-api-key"

agent = Agent([employees_df, salaries_df], memory_size=10)

# Chat with the agent
response = agent.chat("Who gets paid the most?")
print(response)


# Get Clarification Questions
questions = agent.clarification_questions("Who gets paid the most?")
for question in questions:
    print(question)

# Explain how the chat response is generated
response = agent.explain()
print(response)

# Train with data
queries = [
    "Display the distribution of ages in the population.",
    "Visualize the distribution of product ratings.",
    "Show the distribution of household incomes in a region.",
]

codes = [
    "display_age_distribution()",
    "visualize_product_ratings_distribution()",
    "show_household_incomes_distribution_in_region()",
]

agent.train(queries, codes)

print("Done")
