# 🐼 PandasAI

[![Release](https://img.shields.io/pypi/v/pandasai?label=Release&style=flat-square)](https://pypi.org/project/pandasai/)
[![CI](https://github.com/gventuri/pandas-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/gventuri/pandas-ai/actions/workflows/ci.yml/badge.svg)
[![CD](https://github.com/gventuri/pandas-ai/actions/workflows/cd.yml/badge.svg)](https://github.com/gventuri/pandas-ai/actions/workflows/cd.yml/badge.svg)
[![Coverage](https://codecov.io/gh/gventuri/pandas-ai/branch/main/graph/badge.svg)](https://codecov.io/gh/gventuri/pandas-ai)
[![Documentation Status](https://readthedocs.org/projects/pandas-ai/badge/?version=latest)](https://pandas-ai.readthedocs.io/en/latest/?badge=latest)
[![Discord](https://dcbadge.vercel.app/api/server/kF7FqH2FwS?style=flat&compact=true)](https://discord.gg/kF7FqH2FwS)
[![Downloads](https://static.pepy.tech/badge/pandasai)](https://pepy.tech/project/pandasai) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1ZnO-njhL7TBOYPZaqvMvGtsjckZKrv2E?usp=sharing)

PandasAI is a Python library that adds Generative AI capabilities to pandas, the popular data analysis and manipulation tool. It is designed to be used in conjunction with pandas, and is not a replacement for it.

PandasAI makes pandas (and all the most used data analyst libraries) conversational, allowing you to ask questions to your data in natural language. For example, you can ask PandasAI to find all the rows in a DataFrame where the value of a column is greater than 5, and it will return a DataFrame containing only those rows.

You can also ask PandasAI to draw graphs, clean data, impute missing values, and generate features.

## What are the value props of PandasAI?

PandasAI provides two main value props:

- **Ease of use:** PandasAI is designed to be easy to use, even if you are not familiar with generative AI or with `pandas`. You can simply ask questions to your data in natural language, and PandasAI will generate the code to answer your question.
- **Power:** PandasAI can be used to perform a wide variety of tasks, including data exploration, analysis, visualization, cleaning, imputation, and feature engineering.

## How does PandasAI work?

PandasAI works by using a generative AI model to generate Python code. When you ask PandasAI a question, the model will first try to understand the question. Then, it will generate the Python code that would answer the question. Finally, the code will be executed, and the results will be returned to you.

## Who should use PandasAI?

PandasAI is a good choice for anyone who wants to make their data analysis and manipulation workflow more efficient. It is especially useful for people who are not familiar with `pandas`, but also for people who are familiar with it and want to make their workflow more efficient.

## How to get started with PandasAI?

To get started with PandasAI, you first need to install it. You can do this by running the following command:

```console
# Using poetry (recommended)
poetry add pandasai

# Using pip
pip install pandasai
```

Once you have installed PandasAI, you can start using it by importing it into your Python code.
Now you can start asking questions to your data in natural language. For example, the following code will ask PandasAI to find all the rows in a DataFrame where the value of the `gdp` column is greater than 5:

```python
import pandas as pd
from pandasai import SmartDataframe

df = pd.DataFrame({
    "country": [
        "United States", "United Kingdom", "France", "Germany", "Italy", "Spain", "Canada", "Australia", "Japan", "China"],
    "gdp": [
        19294482071552, 2891615567872, 2411255037952, 3435817336832, 1745433788416, 1181205135360, 1607402389504, 1490967855104, 4380756541440, 14631844184064
    ],
})

# Instantiate a LLM
from pandasai.llm import OpenAI
llm = OpenAI(api_token="YOUR_API_TOKEN")  # Get API token from https://platform.openai.com/account/api-keys

df = SmartDataframe(df, config={"llm": llm})
df.chat('Which are the countries with GDP greater than 3000000000000?')
# Output:
# 0    United States
# 3           Germany
# 8             Japan
# 9             China
# Name: country, dtype: object
```

This will return a DataFrame containing only the rows where the value of the `gdp` column is greater than 5.

<!-- add a section for support, where we can add a link to discord -->

## Demo

Try out PandasAI in your browser:

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1ZnO-njhL7TBOYPZaqvMvGtsjckZKrv2E?usp=sharing)

## Support

If you have any questions or need help, please join our **[discord server](https://discord.gg/kF7FqH2FwS)**.

## License

PandasAI is licensed under the MIT License. See the LICENSE file for more details.
