import pandas as pd

from pandasai.ee.agents.semantic_agent import SemanticAgent

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
response = agent.chat("Plot a chart of the average salary of employees by department")
print(response)
