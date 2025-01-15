# ![PandaAI](assets/logo.png)

[![Release](https://img.shields.io/pypi/v/pandasai?label=Release&style=flat-square)](https://pypi.org/project/pandasai/)
[![CI](https://github.com/sinaptik-ai/pandas-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/sinaptik-ai/pandas-ai/actions/workflows/ci.yml/badge.svg)
[![CD](https://github.com/sinaptik-ai/pandas-ai/actions/workflows/cd.yml/badge.svg)](https://github.com/sinaptik-ai/pandas-ai/actions/workflows/cd.yml/badge.svg)
[![Coverage](https://codecov.io/gh/sinaptik-ai/pandas-ai/branch/main/graph/badge.svg)](https://codecov.io/gh/sinaptik-ai/pandas-ai)
[![Discord](https://dcbadge.vercel.app/api/server/kF7FqH2FwS?style=flat&compact=true)](https://discord.gg/KYKj9F2FRH)
[![Downloads](https://static.pepy.tech/badge/pandasai)](https://pepy.tech/project/pandasai) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1ZnO-njhL7TBOYPZaqvMvGtsjckZKrv2E?usp=sharing)

PandaAI is a Python platform that makes it easy to ask questions to your data in natural language. It helps non-technical users to interact with their data in a more natural way, and it helps technical users to save time, and effort when working with data.

# 🔧 Getting started

You can find the full documentation for PandaAI [here](https://pandas-ai.readthedocs.io/en/latest/).

You can either decide to use PandaAI in your Jupyter notebooks, Streamlit apps, or use the client and server architecture from the repo.

## ☁️ Using the platform

![PandaAI](assets/demo.gif) 

## 📚 Using the library

### Python Requirements

Python version `3.8+ <3.12`

### 📦 Installation

You can install the PandaAI library using pip or poetry.

With pip:

```bash
pip install pandasai
```

With poetry:

```bash
poetry add pandasai
```

### 💻 Usage

#### Ask questions

```python
import pandasai as pai

# Sample DataFrame
df = pai.DataFrame({
    "country": ["United States", "United Kingdom", "France", "Germany", "Italy", "Spain", "Canada", "Australia", "Japan", "China"],
    "revenue": [5000, 3200, 2900, 4100, 2300, 2100, 2500, 2600, 4500, 7000]
})

# By default, unless you choose a different LLM, it will use BambooLLM.
# You can get your free API key signing up at https://pandabi.ai (you can also configure it in your .env file)
pai.api_key.set("your-pai-api-key")

df.chat('Which are the top 5 countries by sales?')
```

```
China, United States, Japan, Germany, Australia
```

---

Or you can ask more complex questions:

```python
df.chat(
    "What is the total sales for the top 3 countries by sales?"
)
```

```
The total sales for the top 3 countries by sales is 16500.
```

#### Visualize charts

You can also ask PandaAI to generate charts for you:

```python
df.chat(
    "Plot the histogram of countries showing for each one the gd. Use different colors for each bar",
)
```

![Chart](assets/histogram-chart.png?raw=true)

#### Multiple DataFrames

You can also pass in multiple dataframes to PandaAI and ask questions relating them.

```python
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

employees_df = pai.DataFrame(employees_data)
salaries_df = pai.DataFrame(salaries_data)

# By default, unless you choose a different LLM, it will use BambooLLM.
# You can get your free API key signing up at https://app.pandabi.ai (you can also configure it in your .env file)
pai.api_key.set("your-pai-api-key")

agent = Agent([employees_df, salaries_df])
agent.chat("Who gets paid the most?")
```

```
Olivia gets paid the most.
```

You can find more examples in the [examples](examples) directory.

## 📜 License

PandaAI is available under the MIT expat license, except for the `pandasai/ee` directory (which has it's [license here](https://github.com/Sinaptik-AI/pandas-ai/blob/master/pandasai/ee/LICENSE) if applicable.

If you are interested in managed PandaAI Cloud or self-hosted Enterprise Offering, [contact us](https://forms.gle/JEUqkwuTqFZjhP7h8).

## Resources

- [Docs](https://pandas-ai.readthedocs.io/en/latest/) for comprehensive documentation
- [Examples](examples) for example notebooks
- [Discord](https://discord.gg/KYKj9F2FRH) for discussion with the community and PandaAI team

## 🤝 Contributing

Contributions are welcome! Please check the outstanding issues and feel free to open a pull request.
For more information, please check out the [contributing guidelines](CONTRIBUTING.md).

### Thank you!

[![Contributors](https://contrib.rocks/image?repo=sinaptik-ai/pandas-ai)](https://github.com/sinaptik-ai/pandas-ai/graphs/contributors)
