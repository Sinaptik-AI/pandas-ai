# Usage

## Installation

To use `pandasai`, first install it

```console
# Using poetry (recommended)
poetry add pandasai

# Using pip
pip install pandasai
```

> Before you install it, we recommended to create a Virtual environment using your preffred choice of Environment Managers e.g [Poetry](https://python-poetry.org/), [Pipenv](https://pipenv.pypa.io/en/latest/), [Conda](https://docs.conda.io/en/latest/), [Virtualenv](https://virtualenv.pypa.io/en/latest/), [Venv](https://docs.python.org/3/library/venv.html) etc.

### Optional Installs

To keep the package size small, we have decided to make some dependencies that are not required by default. These dependencies are required for some features of `pandasai`. To install `pandasai` with these extra dependencies, run

```console
pip install pandasai[extra-dependency-name]
```

You can replace `extra-dependency-name` with any of the following:

- `google-aip`: this extra dependency is required if you want to use Google PaLM as a language model.
- `google-sheet`: this extra dependency is required if you want to use Google Sheets as a data source.
- `excel`: this extra dependency is required if you want to use Excel files as a data source.
- `polars`: this extra dependency is required if you want to use Polars dataframes as a data source.
- `langchain`: this extra dependency is required if you want to support the LangChain LLMs.
- `numpy`: this extra dependency is required if you want to support numpy.
- `ggplot`: this extra dependency is required if you want to support ggplot for plotting.
- `seaborn`: this extra dependency is required if you want to support seaborn for plotting.
- `plotly`: this extra dependency is required if you want to support plotly for plotting.
- `statsmodels`: this extra dependency is required if you want to support statsmodels.
- `scikit-learn`: this extra dependency is required if you want to support scikit-learn.
- `streamlit`: this extra dependency is required if you want to support the streamlit.

## SmartDataframe

Below is simple example to get started with `pandasai`.

```python
import pandas as pd
from pandasai import SmartDataframe

# Sample DataFrame
df = pd.DataFrame({
    "country": ["United States", "United Kingdom", "France", "Germany", "Italy", "Spain", "Canada", "Australia", "Japan", "China"],
    "gdp": [19294482071552, 2891615567872, 2411255037952, 3435817336832, 1745433788416, 1181205135360, 1607402389504, 1490967855104, 4380756541440, 14631844184064],
    "happiness_index": [6.94, 7.16, 6.66, 7.07, 6.38, 6.4, 7.23, 7.22, 5.87, 5.12]
})

# Instantiate a LLM
from pandasai.llm import OpenAI
llm = OpenAI(api_token="YOUR_API_TOKEN")

df = SmartDataframe(df, config={"llm": llm})
df.chat('Which are the 5 happiest countries?')
# Output: United Kingdom, Canada, Australia, United States, Germany
```

If you want to get to know more about the `SmartDataframe` class, check out this video:

[![Intro to SmartDataframe](https://cdn.loom.com/sessions/thumbnails/1ec1b8fbaa0e4ae0ab99b728b8b05fdb-00001.jpg)](https://www.loom.com/embed/1ec1b8fbaa0e4ae0ab99b728b8b05fdb?sid=7370854b-57c3-4f00-801b-69811a98d970 "Intro to SmartDataframe")

### How to generate OpenAI API Token

Users are required to generate `YOUR_API_TOKEN`. Follow below simple steps to generate your API_TOKEN with
[openai](https://platform.openai.com/overview).

1. Go to https://openai.com/api/ and signup with your email address or connect your Google Account.
2. Go to View API Keys on left side of your Personal Account Settings
3. Select Create new Secret key

> The API access to openai is a paid service. You have to set up billing.
> Read the [Pricing](https://platform.openai.com/docs/quickstart/pricing) information before experimenting.

## SmartDatalake

PandasAI also supports queries with multiple dataframes. To perform such queries, you can use a `SmartDatalake` instead of a `SmartDataframe`. A `SmartDatalake` is a collection of `SmartDataframe`s. You can instantiate a `SmartDatalake` as follows:

```python
from pandasai import SmartDatalake
import pandas as pd

# Sample DataFrames
df1 = pd.DataFrame({
    "country": ["United States", "United Kingdom", "France", "Germany", "Italy", "Spain", "Canada", "Australia", "Japan", "China"],
    "gdp": [19294482071552, 2891615567872, 2411255037952, 3435817336832, 1745433788416, 1181205135360, 1607402389504, 1490967855104, 4380756541440, 14631844184064],
    "happiness_index": [6.94, 7.16, 6.66, 7.07, 6.38, 6.4, 7.23, 7.22, 5.87, 5.12]
})
df2 = "data/Loan payments data.csv"
df3 = "data/Loan payments data.xlsx"

dl = SmartDatalake([df1, df2, df3])
```

Then, you can use the `SmartDatalake` as follows, similar to how you would use a `SmartDataframe`:

```python
dl.chat('Which are the 5 happiest countries?')
# Output: United Kingdom, Canada, Australia, United States, Germany
```

PandasAI will automatically figure out which dataframe or dataframes are relevant to the query and will use only those dataframes to answer the query.

[![Intro to SmartDatalake](https://cdn.loom.com/sessions/thumbnails/a2006ac27b0545189cb5b9b2e011bc72-00001.jpg)](https://www.loom.com/share/a2006ac27b0545189cb5b9b2e011bc72 "Intro to SmartDatalake")

## Agent

PandasAI also supports agents. While a `SmartDataframe` or a `SmartDatalake` can be used to answer a single query and are meant to be used in a single session and for exploratory data analysis, an agent can be used for multi-turn conversations and for production use cases. You can instantiate an agent as follows:

```python
from pandasai import Agent
import pandas as pd

# Sample DataFrames
df1 = pd.DataFrame({
    "country": ["United States", "United Kingdom", "France", "Germany", "Italy", "Spain", "Canada", "Australia", "Japan", "China"],
    "gdp": [19294482071552, 2891615567872, 2411255037952, 3435817336832, 1745433788416, 1181205135360, 1607402389504, 1490967855104, 4380756541440, 14631844184064],
    "happiness_index": [6.94, 7.16, 6.66, 7.07, 6.38, 6.4, 7.23, 7.22, 5.87, 5.12]
})

agent = Agent([df1])
```

Then, you can use the agent as follows:

```python
agent.chat('Which are the 5 happiest countries?')
# Output: United Kingdom, Canada, Australia, United States, Germany
```

Contrary to a `SmartDataframe` or a `SmartDatalake`, an agent will keep track of the state of the conversation and will be able to answer multi-turn conversations. For example:

```python
agent.chat('And what is the GDP of these countries?')
# Output: 2891615567872, 1607402389504, 1490967855104, 19294482071552, 3435817336832
```

### Clarification questions

An agent will also be able to ask clarification questions if it does not have enough information to answer the query. For example:

```python
agent.clarification_question('What is the GDP of the United States?')
```

this will return up to 3 clarification questions that the agent can ask to the user to get more information to answer the query.

### Explanation

An agent will also be able to explain the answer to the user. For example:

```python
response = agent.chat('What is the GDP of the United States?')
explanation = agent.explain()

print("The answer is", response)
print("The explanation is", explanation)
```

### Rephrase Question

Rephrase question to get accurate and comprehensive response from the model. For example:

```python
rephrased_query = agent.rephrase_query('What is the GDP of the United States?')

print("The answer is", rephrased_query)

```

## Config

When you instantiate a `SmartDataframe`, you can pass a `config` object as the second argument. This object can contain custom settings that will be used by `pandasai` when generating code.

As an alternative, you can simply edit the `pandasai.json` file in the root of your project. This file will be automatically loaded by `pandasai` and these will be the default settings. You will still be able to override these settings by passing the settings that you want to override when instantiating a `SmartDataframe`.

Settings:

- `llm`: the LLM to use. You can pass an instance of an LLM or the name of an LLM. You can use one of the LLMs supported. You can find more information about LLMs [here](./LLMs/llms.md).
- `llm_options`: the options to use for the LLM (for example the api token, etc). You can find more information about the settings [here](./LLMs/llms.md).
- `save_logs`: whether to save the logs of the LLM. Defaults to `True`. You will find the logs in the `pandasai.log` file in the root of your project.
- `verbose`: whether to print the logs in the console as PandasAI is executed. Defaults to `False`.
- `enforce_privacy`: whether to enforce privacy. Defaults to `False`. If set to `True`, PandasAI will not send any data to the LLM, but only the metadata. By default, PandasAI will send 5 samples that are anonymized to improve the accuracy of the results.
- `save_charts`: whether to save the charts generated by PandasAI. Defaults to `False`. You will find the charts in the root of your project or in the path specified by `save_charts_path`.
- `save_charts_path`: the path where to save the charts. Defaults to `exports/charts/`. You can use this setting to override the default path.
- `enable_cache`: whether to enable caching. Defaults to `True`. If set to `True`, PandasAI will cache the results of the LLM to improve the response time. If set to `False`, PandasAI will always call the LLM.
- `use_error_correction_framework`: whether to use the error correction framework. Defaults to `True`. If set to `True`, PandasAI will try to correct the errors in the code generated by the LLM with further calls to the LLM. If set to `False`, PandasAI will not try to correct the errors in the code generated by the LLM.
- `use_advanced_reasoning_framework`: whether to use the advanced reasoning framework. Defaults to `False`. If set to `True`, PandasAI will try to use advanced reasoning to improve the results of the LLM and provide an explanation for the results.
- `max_retries`: the maximum number of retries to use when using the error correction framework. Defaults to `3`. You can use this setting to override the default number of retries.
- `custom_prompts`: the custom prompts to use. Defaults to `{}`. You can use this setting to override the default custom prompts. You can find more information about custom prompts [here](custom-prompts.md).
- `custom_whitelisted_dependencies`: the custom whitelisted dependencies to use. Defaults to `{}`. You can use this setting to override the default custom whitelisted dependencies. You can find more information about custom whitelisted dependencies [here](custom-whitelisted-dependencies.md).
- `middlewares`: the middlewares to use. Defaults to `[]`. You can use this setting to override the default middlewares. You can find more information about middlewares [here](middlewares.md).
- `callback`: the callback to use. Defaults to `None`. You can use this setting to override the default callback. You can find more information about callbacks [here](callbacks.md).

## Demo in Google Colab

Try out PandasAI in your browser:

[![Open in Colab](https://camo.githubusercontent.com/84f0493939e0c4de4e6dbe113251b4bfb5353e57134ffd9fcab6b8714514d4d1/68747470733a2f2f636f6c61622e72657365617263682e676f6f676c652e636f6d2f6173736574732f636f6c61622d62616467652e737667)](https://colab.research.google.com/drive/1ZnO-njhL7TBOYPZaqvMvGtsjckZKrv2E?usp=sharing)

## Examples

You can find some examples [here](examples.md).

```

```
