# Train with your own settings

You can train PandasAI to understand your data better and to improve its performance. Training is as easy as calling the `train` method on the `SmartDataframe`, `SmartDatalake` or `Agent`.

There are two kinds of training:

- instructions training
- q/a training

## Instructions training

Instructions training is used to teach PandasAI how you expect it to respond to certain queries. You can provide generic instructions about how you expect the model to approach certain types of queries, and PandasAI will use these instructions to generate responses to similar queries.

For example, you might want the LLM to be aware that your company's fiscal year starts in April, or about specific ways you want to handle missing data. Or you might want to teach it about specific business rules or data analysis best practices that are specific to your organization.

To train PandasAI with instructions, you can use the `train` method on the `Agent`, `SmartDataframe` or `SmartDatalake`, as it follows:

```python
from pandasai import Agent

df = Agent("data.csv")
df.train(docs="The fiscal year starts in April")

response = df.chat("What is the total sales for the fiscal year?")
print(response)
# The model will use the information provided in the training to generate a response
```

Your training data is persisted, so you only need to train the model once.

## Q/A training

Q/A training is used to teach PandasAI the desired process to answer specific questions, enhancing the model's performance and determinism. One of the biggest challenges with LLMs is that they are not deterministic, meaning that the same question can produce different answers at different times. Q/A training can help to mitigate this issue.

To train PandasAI with Q/A, you can use the `train` method on the `Agent`, `SmartDataframe` or `SmartDatalake`, as it follows:

```python
from pandasai import Agent

df = Agent("data.csv")

# Train the model
query = "What is the total sales for the current fiscal year?"
response = """
import pandas as pd

df = dfs[0]

# Calculate the total sales for the current fiscal year
total_sales = df[df['date'] >= pd.to_datetime('today').replace(month=4, day=1)]['sales'].sum()
result = { "type": "number", "value": total_sales }
"""
df.train(queries=[query], codes=[response])

response = df.chat("What is the total sales for the last fiscal year?")
print(response)
# The model will use the information provided in the training to generate a response
```

Also in this case, your training data is persisted, so you only need to train the model once.
