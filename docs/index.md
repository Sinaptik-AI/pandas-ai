# ![PandasAI](https://github.com/Sinaptik-AI/pandas-ai/blob/main/images/logo.png?raw=true)

[![Release](https://img.shields.io/pypi/v/pandasai?label=Release&style=flat-square)](https://pypi.org/project/pandasai/)
[![CI](https://github.com/gventuri/pandas-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/gventuri/pandas-ai/actions/workflows/ci.yml/badge.svg)
[![CD](https://github.com/gventuri/pandas-ai/actions/workflows/cd.yml/badge.svg)](https://github.com/gventuri/pandas-ai/actions/workflows/cd.yml/badge.svg)
[![Coverage](https://codecov.io/gh/gventuri/pandas-ai/branch/main/graph/badge.svg)](https://codecov.io/gh/gventuri/pandas-ai)
[![Documentation Status](https://readthedocs.org/projects/pandas-ai/badge/?version=latest)](https://pandas-ai.readthedocs.io/en/latest/?badge=latest)
[![Discord](https://dcbadge.vercel.app/api/server/kF7FqH2FwS?style=flat&compact=true)](https://discord.gg/kF7FqH2FwS)
[![Downloads](https://static.pepy.tech/badge/pandasai)](https://pepy.tech/project/pandasai) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1ZnO-njhL7TBOYPZaqvMvGtsjckZKrv2E?usp=sharing)

PandasAI is a Python library that makes it easy to ask questions to your data (CSV, XLSX, PostgreSQL, MySQL, BigQuery, Databrick, Snowflake, etc.) in natural language. xIt helps you to explore, clean, and analyze your data using generative AI.

Beyond querying, PandasAI offers functionalities to visualize data through graphs, cleanse datasets by addressing missing values, and enhance data quality through feature generation, making it a comprehensive tool for data scientists and analysts.

## Features

- **Natural language querying**: Ask questions to your data in natural language.
- **Data visualization**: Generate graphs and charts to visualize your data.
- **Data cleansing**: Cleanse datasets by addressing missing values.
- **Feature generation**: Enhance data quality through feature generation.
- **Data connectors**: Connect to various data sources like CSV, XLSX, PostgreSQL, MySQL, BigQuery, Databrick, Snowflake, etc.

## How does PandasAI work?

PandasAI uses a generative AI model to understand and interpret natural language queries and translate them into python code and SQL queries. It then uses the code to interact with the data and return the results to the user.

## Who should use PandasAI?

PandasAI is designed for data scientists, analysts, and engineers who want to interact with their data in a more natural way. It is particularly useful for those who are not familiar with SQL or Python or who want to save time and effort when working with data. It is also useful for those who are familiar with SQL and Python, as it allows them to ask questions to their data without having to write any complex code.

## How to get started with PandasAI?

To get started with PandasAI, you first need to install it. You can do this by running the following command:

```bash
# Using poetry (recommended)
poetry add pandasai

# Using pip
pip install pandasai
```

Once you have installed PandasAI, you can start using it by importing the `SmartDataframe` class and instantiating it with your data. You can then use the `chat` method to ask questions to your data in natural language.

```python
import pandas as pd
from pandasai import SmartDataframe

# Sample DataFrame
sales_by_country = pd.DataFrame({
    "country": ["United States", "United Kingdom", "France", "Germany", "Italy", "Spain", "Canada", "Australia", "Japan", "China"],
    "sales": [5000, 3200, 2900, 4100, 2300, 2100, 2500, 2600, 4500, 7000]
})

# Instantiate a LLM
from pandasai.llm import OpenAI
llm = OpenAI(api_token="YOUR_API_TOKEN")

df = SmartDataframe(sales_by_country, config={"llm": llm})
df.chat('Which are the top 5 countries by sales?')
## Output
# China, United States, Japan, Germany, Australia
```

## Demo

Try out PandasAI yourself in your browser:

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1ZnO-njhL7TBOYPZaqvMvGtsjckZKrv2E?usp=sharing)

## Support

If you have any questions or need help, please join our **[discord server](https://discord.gg/kF7FqH2FwS)**.

## License

PandasAI is available under the MIT expat license, except for the `pandasai/ee` directory (which has it's [license here](https://github.com/Sinaptik-AI/pandas-ai/blob/master/pandasai/ee/LICENSE) if applicable.

If you are interested in managed PandasAI Cloud or self-hosted Enterprise Offering, take a look at [our website](https://pandas-ai.com) or [book a meeting with us](https://zcal.co/gventuri/pandas-ai-demo).
