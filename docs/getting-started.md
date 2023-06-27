# Usage

`pandasai` is developed on top of `pandas` api. The objective is to make dataframe conversation
using Large Language Models (LLMs).

## Installation

To use `pandasai`, first install it using pip through [PyPi](https://pypi.org/project/pandasai/) package distribution
framework. It is actively developed so be vigilant for versions updates.

```console
pip install pandasai
```

> It is recommended to create a Virtual environment using your preffred choice of Environment Managers e.g conda,
> Poetry etc

### Optional Installs

`pandasai` optionally supports Google PaLM. To install `pandasai` with this extra dependency, run

```console
pip install pandasai[google]
```

## Getting Started

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

pandas_ai = PandasAI(llm)
pandas_ai(df, prompt='Which are the 5 happiest countries?')
```

## Generate openai API Token

Users are required to generate `YOUR_API_TOKEN`. Follow below simple steps to generate your API_TOKEN with
[openai](https://platform.openai.com/overview).

1. Go to https://openai.com/api/ and signup with your email address or connect your Google Account.
2. Go to View API Keys on left side of your Personal Account Settings
3. Select Create new Secret key

> The API access to openai is a paid service. You have to set up billing.
> Read the [Pricing](https://platform.openai.com/docs/quickstart/pricing) information before experimenting.

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
pandas_ai = PandasAI(llm, verbose=True, conversational=True)
response = pandas_ai(df, "How many loans are from men and have been paid off?")
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
pandas_ai = PandasAI(llm, verbose=True)
response = pandas_ai(df, "Calculate the sum of the gdp of north american countries")
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
response = pandas_ai(
    df,
    "Plot the histogram of countries showing for each the gpd, using different colors for each bar",
)
print(response)
# Output: check out images/histogram-chart.png
```

#### Saving Plots with User Defined Path

Below is the example to Save Charts with user defined location. 

```python
import pandas as pd
import os
from data.sample_dataframe import dataframe

from pandasai import PandasAI
from pandasai.llm.openai import OpenAI

df = pd.DataFrame(dataframe)

llm = OpenAI()

user_defined_path = os.getcwd()
pandas_ai = PandasAI(llm, save_charts=True,
                     save_charts_path=user_defined_path,
                     verbose=True)
response = pandas_ai(
    df,
    "Plot the histogram of countries showing for each the gpd,"
    " using different colors for each bar",
)
# Output: check out $pwd/exports/charts/{hashid}/chart.png
```

### Working with multiple dataframes

Example of using PandasAI with multiple Pandas DataFrames

```python
import pandas as pd

from pandasai import PandasAI
from pandasai.llm.openai import OpenAI

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

llm = OpenAI()
pandas_ai = PandasAI(llm, verbose=True)
response = pandas_ai(
    [employees_df, salaries_df],
    "Who gets paid the most?",
)
print(response)
# Output: Olivia gets paid the most.
```

### Chain of commands

You can chain commands by passing the output of one command to the next one. In the example, we first filter the original
dataframe by gender and then by loans that have been paid off.

```python
import pandas as pd

from pandasai import PandasAI
from pandasai.llm.openai import OpenAI

df = pd.read_csv("examples/data/Loan payments data.csv")

llm = OpenAI()
pandas_ai = PandasAI(llm, verbose=True)

# We filter by males only
from_males_df = pandas_ai(df, "Filter the dataframe by males")
paid_from_males_df = pandas_ai(from_males_df, "Filter the dataframe by loans that have been paid off")
print(paid_from_males_df)
# Output:
# [247 rows x 11 columns]
#          Loan_ID loan_status  Principal  terms effective_date    due_date     paid_off_time  past_due_days  age             education Gender
# 0    xqd20166231     PAIDOFF       1000     30       9/8/2016   10/7/2016   9/14/2016 19:31            NaN   45  High School or Below   male
# 3    xqd20160004     PAIDOFF       1000     15       9/8/2016   9/22/2016   9/22/2016 20:00            NaN   27               college   male
# 5    xqd20160706     PAIDOFF        300      7       9/9/2016   9/15/2016    9/9/2016 13:45            NaN   35       Master or Above   male
# 6    xqd20160007     PAIDOFF       1000     30       9/9/2016   10/8/2016   10/7/2016 23:07            NaN   29               college   male
# 7    xqd20160008     PAIDOFF       1000     30       9/9/2016   10/8/2016   10/5/2016 20:33            NaN   36               college   male
# ..           ...         ...        ...    ...            ...         ...               ...            ...  ...                   ...    ...
# 294  xqd20160295     PAIDOFF       1000     30      9/14/2016  10/13/2016  10/13/2016 13:00            NaN   36              Bechalor   male
# 296  xqd20160297     PAIDOFF        800     15      9/14/2016   9/28/2016    9/21/2016 4:42            NaN   27               college   male
# 297  xqd20160298     PAIDOFF       1000     30      9/14/2016  10/13/2016   10/13/2016 9:00            NaN   29  High School or Below   male
# 298  xqd20160299     PAIDOFF       1000     30      9/14/2016  10/13/2016   10/13/2016 9:00            NaN   40  High School or Below   male
# 299  xqd20160300     PAIDOFF       1000     30      9/14/2016  10/13/2016  10/13/2016 11:00            NaN   28               college   male

# [247 rows x 11 columns]
```
