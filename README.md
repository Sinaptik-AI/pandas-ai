# ![PandasAI](assets/logo.png)

[![Release](https://img.shields.io/pypi/v/pandasai?label=Release&style=flat-square)](https://pypi.org/project/pandasai/)
[![CI](https://github.com/gventuri/pandas-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/gventuri/pandas-ai/actions/workflows/ci.yml/badge.svg)
[![CD](https://github.com/gventuri/pandas-ai/actions/workflows/cd.yml/badge.svg)](https://github.com/gventuri/pandas-ai/actions/workflows/cd.yml/badge.svg)
[![Coverage](https://codecov.io/gh/gventuri/pandas-ai/branch/main/graph/badge.svg)](https://codecov.io/gh/gventuri/pandas-ai)
[![Discord](https://dcbadge.vercel.app/api/server/kF7FqH2FwS?style=flat&compact=true)](https://discord.gg/kF7FqH2FwS)
[![Downloads](https://static.pepy.tech/badge/pandasai)](https://pepy.tech/project/pandasai) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1ZnO-njhL7TBOYPZaqvMvGtsjckZKrv2E?usp=sharing)

PandasAI is a Python platform that makes it easy to ask questions to your data in natural language. It helps non-technical users to interact with their data in a more natural way, and it helps technical users to save time and effort when working with data.

# 🚀 Deploying PandasAI

PandasAI can be used in a variety of ways. You can easily use it in your Jupyter notebooks or streamlit apps, or you can deploy it as a REST API such as with FastAPI or Flask.

If you are interested in the managed PandasAI Cloud or our self-hosted Enterprise Offering, [contact us](https://forms.gle/JEUqkwuTqFZjhP7h8).

# 🔧 Getting started

You can find the full documentation for PandasAI [here](https://pandas-ai.readthedocs.io/en/latest/).

You can either decide to use PandasAI in your Jupyter notebooks, streamlit apps, or use the client and server architecture from the repo.

## ☁️ Using the platform

[![PandasAI platform](assets/demo.gif?raw=true)](https://www.youtube.com/watch?v=kh61wEy9GYM)

### 📦 Installation

PandasAI platform is uses a dockerized client-server architecture. You will need to have Docker installed in your machine.

```bash
git clone https://github.com/sinaptik-ai/pandas-ai/
cd pandas-ai
docker-compose build
```

### 🚀 Running the platform

Once you have built the platform, you can run it with:

```bash
docker-compose up
```

This will start the client and server, and you can access the client at `http://localhost:3000`.

## 📚 Using the library

### 📦 Installation

You can install the PandasAI library using pip or poetry.

With pip:

```bash
pip install pandasai
```

With poetry:

```bash
poetry add pandasai
```

### 🔍 Demo

Try out the PandasAI library yourself in your browser:

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1ZnO-njhL7TBOYPZaqvMvGtsjckZKrv2E?usp=sharing)

### 💻 Usage

#### Ask questions

```python
import os
import pandas as pd
from pandasai import Agent

# Sample DataFrame
sales_by_country = pd.DataFrame({
    "country": ["United States", "United Kingdom", "France", "Germany", "Italy", "Spain", "Canada", "Australia", "Japan", "China"],
    "revenue": [5000, 3200, 2900, 4100, 2300, 2100, 2500, 2600, 4500, 7000]
})

# By default, unless you choose a different LLM, it will use BambooLLM.
# You can get your free API key signing up at https://pandabi.ai (you can also configure it in your .env file)
os.environ["PANDASAI_API_KEY"] = "YOUR_API_KEY"

agent = Agent(sales_by_country)
agent.chat('Which are the top 5 countries by sales?')
```

```
China, United States, Japan, Germany, Australia
```

---

Or you can ask more complex questions:

```python
agent.chat(
    "What is the total sales for the top 3 countries by sales?"
)
```

```
The total sales for the top 3 countries by sales is 16500.
```

#### Visualize charts

You can also ask PandasAI to generate charts for you:

```python
agent.chat(
    "Plot the histogram of countries showing for each one the gd. Use different colors for each bar",
)
```

![Chart](assets/histogram-chart.png?raw=true)

#### Multiple DataFrames

You can also pass in multiple dataframes to PandasAI and ask questions relating them.

```python
import os
import pandas as pd
from pandasai import Agent

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

# By default, unless you choose a different LLM, it will use BambooLLM.
# You can get your free API key signing up at https://pandabi.ai (you can also configure it in your .env file)
os.environ["PANDASAI_API_KEY"] = "YOUR_API_KEY"

agent = Agent([employees_df, salaries_df])
agent.chat("Who gets paid the most?")
```

```
Olivia gets paid the most.
```

You can find more examples in the [examples](examples) directory.

## 🔒 Privacy & Security

In order to generate the Python code to run, we take some random samples from the dataframe, we randomize it (using random generation for sensitive data and shuffling for non-sensitive data) and send just the randomized head to the LLM.

If you want to enforce further your privacy you can instantiate PandasAI with `enforce_privacy = True` which will not send the head (but just column names) to the LLM.

## 📜 License

PandasAI is available under the MIT expat license, except for the `pandasai/ee` directory (which has it's [license here](https://github.com/Sinaptik-AI/pandas-ai/blob/master/pandasai/ee/LICENSE) if applicable.

If you are interested in managed PandasAI Cloud or self-hosted Enterprise Offering, [contact us](https://forms.gle/JEUqkwuTqFZjhP7h8).

## Resources

- [Docs](https://pandas-ai.readthedocs.io/en/latest/) for comprehensive documentation
- [Examples](examples) for example notebooks
- [Discord](https://discord.gg/kF7FqH2FwS) for discussion with the community and PandasAI team

## 🤝 Contributing

Contributions are welcome! Please check the outstanding issues and feel free to open a pull request.
For more information, please check out the [contributing guidelines](CONTRIBUTING.md).

### Thank you!

[![Contributors](https://contrib.rocks/image?repo=gventuri/pandas-ai)](https://github.com/gventuri/pandas-ai/graphs/contributors)
