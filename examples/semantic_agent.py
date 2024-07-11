import pandas as pd
import os
from pandasai.ee.agents.semantic_agent import SemanticAgent
from pandasai.exceptions import InvalidLLMOutputType





os.environ["PANDASAI_API_KEY"] = "api_key_here"

config_ = {"enable_cache": False, "direct_sql": True}

salaries_df = pd.DataFrame(
    {
        "EmployeeID": [1, 2, 3, 4, 5],
        "Salary": [5000, 6000, 4500, 7000, 5500],
    }
)

employees_df = pd.DataFrame(
    {
        "EmployeeID": [1, 2, 3, 4, 5],
        "Name": ["John", "Emma", "Liam", "Olivia", "William"],
        "Department": ["HR", "Marketing", "IT", "Marketing", "Finance"],
    }
)

schema = [
    {
        "name": "Employees",
        "table": "Employees",
        "measures": [{"name": "count", "type": "count", "sql": "EmployeeID"}],
        "dimensions": [
            {"name": "EmployeeID", "type": "string", "sql": "EmployeeID"},
            {"name": "Department", "type": "string", "sql": "Department"},
        ],
        "joins": [
            {
                "name": "Salaries",
                "join_type": "left",
                "sql": "Employees.EmployeeID = Salaries.EmployeeID",
            }
        ],
    },
    {
        "name": "Salaries",
        "table": "Salaries",
        "measures": [
            {"name": "count", "type": "count", "sql": "EmployeeID"},
            {"name": "avg_salary", "type": "avg", "sql": "Salary"},
            {"name": "max_salary", "type": "max", "sql": "Salary"},
        ],
        "dimensions": [
            {"name": "EmployeeID", "type": "string", "sql": "EmployeeID"},
            {"name": "Salary", "type": "string", "sql": "Salary"},
        ],
        "joins": [
            {
                "name": "Employees",
                "join_type": "left",
                "sql": "Contracts.contract_code = Fees.contract_id",
            }
        ],
    },
]




agent = SemanticAgent([employees_df, salaries_df], config=config_, schema=schema)

# Chat with the agent
# response = agent.chat("Plot a chart of the average salary of employees by department")
# print(response)




# Testing with a simple DataFrame
df = pd.DataFrame(columns=["Empdata"], data=[[1], [2]])

df.head()


try:
    #  Create an instance of the SemanticAgent with the provided dataframe
    semantic_agent = SemanticAgent(dfs=df)
    #  Print the generated schema
    print(semantic_agent._schema)
except InvalidLLMOutputType as e:
    #  If the LLM fails to generate a valid schema, catch the InvalidLLMOutputType exception
    print(f"Error: {e}")  # Print the error message
    print("Using fallback schema...")  # Inform the user that a fallback schema will be used


# Here, you can provide a fallback schema or take appropriate action
# For example, you can define a default schema and assign it to semantic_agent._schema
# fallback_schema = [...]
# semantic_agent._schema = fallback_schema