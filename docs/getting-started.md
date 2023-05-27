Usage
=====
`pandasai` is developed on top of `pandas` api. The objective is to make dataframe conversation 
using Large Language Models (LLMs).

Installation
------------

To use pandasai, first install it using pip through [PyPi](https://pypi.org/project/pandasai/) package distribution 
framework. It is actively developed so be vigilant for versions updates.

```console
pip install pandasai
```

>It is recommended to create a Virtual environment using your preffred choice of Environment Managers e.g conda, 
>Poetry etc

Getting Started
---------------
Below is simple example to get started with `pandasai`.

```python
import pandas as pd
from pandasai import PandasAI

# Sample DataFrame
df = pd.DataFrame({
    "country": ["United States", "United Kingdom", "France", "Germany", "Italy", "Spain", "Canada", "Australia", "Japan", "China"],
    "gdp": [19294482071552, 2891615567872, 2411255037952, 3435817336832, 1745433788416, 1181205135360, 1607402389504, 1490967855104, 4380756541440, 14631844184064],
    "happiness_index": [6.94, 7.16, 6.66, 7.07, 6.38, 6.4, 7.23, 7.22, 5.87, 5.12]
})

# Instantiate a LLM
from pandasai.llm.openai import OpenAI
llm = OpenAI(api_token="YOUR_API_TOKEN")

pandas_ai = PandasAI(llm, conversational=False)
pandas_ai.run(df, prompt='Which are the 5 happiest countries?')
```

## Generate openai API Token

Users are required to generate `YOUR_API_TOKEN`. Follow below simple steps to generate your API_TOKEN with 
[openai](https://platform.openai.com/overview).

1. Go to  https://openai.com/api/ and signup with your email address or connect your Google Account.
2. Go to View API Keys on left side of your Personal Account Settings
3. Select Create new Secret key

> The API access to openai is a paid service. You have to set up billing. 
>Read the [Pricing](https://platform.openai.com/docs/quickstart/pricing) information before experimenting.


## Demo in Google Colab

Try out PandasAI in your browser:

[![Open in Colab](https://camo.githubusercontent.com/84f0493939e0c4de4e6dbe113251b4bfb5353e57134ffd9fcab6b8714514d4d1/68747470733a2f2f636f6c61622e72657365617263682e676f6f676c652e636f6d2f6173736574732f636f6c61622d62616467652e737667)](https://colab.research.google.com/drive/1rKz7TudOeCeKGHekw7JFNL4sagN9hon-?usp=sharing)

### Examples 
Other [examples](../examples) are included in the repository along with samples of data.

#### Working with CSV

Example of using PandasAI with a CSV file

```python
import pandas as pd

from pandasai import PandasAI
from pandasai.llm.openai import OpenAI

df = pd.read_csv("data/Loan payments data.csv")

llm = OpenAI()
pandas_ai = PandasAI(llm, verbose=True)
response = pandas_ai.run(df, "How many loans are from men and have been paid off?")
print(response)
# Output: 247 loans have been paid off by men.
```

#### Working is Pandas Dataframe
Example of using PandasAI with a Pandas DataFrame
```python
import pandas as pd
from data.sample_dataframe import dataframe

from pandasai import PandasAI
from pandasai.llm.openai import OpenAI

df = pd.DataFrame(dataframe)

llm = OpenAI()
pandas_ai = PandasAI(llm, verbose=True, conversational=False)
response = pandas_ai.run(df, "Calculate the sum of the gdp of north american countries")
print(response)
# Output: 20901884461056

```

#### Plotting 
Example of using PandasAI to generate a chart from a Pandas DataFrame
```python
import pandas as pd
from data.sample_dataframe import dataframe

from pandasai import PandasAI
from pandasai.llm.openai import OpenAI

df = pd.DataFrame(dataframe)

llm = OpenAI()
pandas_ai = PandasAI(llm)
response = pandas_ai.run(
    df,
    "Plot the histogram of countries showing for each the gpd, using different colors for each bar",
)
print(response)
# Output: check out images/histogram-chart.png
```