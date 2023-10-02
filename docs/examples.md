# Examples

Some examples of using PandasAI with different data sources.
Other [examples](../examples) are included in the repository along with samples of data.

## Working with pandas dataframes

Example of using PandasAI with a Pandas DataFrame

```python
from pandasai import SmartDataframe
import pandas as pd

# pandas dataframe
df = pd.DataFrame({
    "country": ["United States", "United Kingdom", "France", "Germany", "Italy", "Spain", "Canada", "Australia", "Japan", "China"],
    "gdp": [19294482071552, 2891615567872, 2411255037952, 3435817336832, 1745433788416, 1181205135360, 1607402389504, 1490967855104, 4380756541440, 14631844184064],
    "happiness_index": [6.94, 7.16, 6.66, 7.07, 6.38, 6.4, 7.23, 7.22, 5.87, 5.12]
})

# convert to SmartDataframe
df = SmartDataframe(df)

df.chat('Calculate the sum of the gdp of north american countries')
print(response)
# Output: 20901884461056
```

## Working with CSVs

Example of using PandasAI with a CSV file

```python
from pandasai import SmartDataframe

# You can instantiate a SmartDataframe with a path to a CSV file
df = Smartdataframe("data/Loan payments data.csv")

df.chat("How many loans are from men and have been paid off?")
print(response)
# Output: 247 loans have been paid off by men.
```

## Working with Excel files

Example of using PandasAI with an Excel file. In order to use Excel files as a data source, you need to install the `pandasai[excel]` extra dependency.

```console
pip install pandasai[excel]
```

Then, you can use PandasAI with an Excel file as follows:

```python
from pandasai import SmartDataframe

# You can instantiate a SmartDataframe with a path to an Excel file
df = Smartdataframe("data/Loan payments data.xlsx")

df.chat("How many loans are from men and have been paid off?")
print(response)
# Output: 247 loans have been paid off by men.
```

## Working with Google Sheets

Example of using PandasAI with a Google Sheet. In order to use Google Sheets as a data source, you need to install the `pandasai[google-sheet]` extra dependency.

```console
pip install pandasai[google-sheet]
```

Then, you can use PandasAI with a Google Sheet as follows:

```python
from pandasai import SmartDataframe

# You can instantiate a SmartDataframe with a path to a Google Sheet
df = Smartdataframe("https://docs.google.com/spreadsheets/d/fake/edit#gid=0")
df.chat("How many loans are from men and have been paid off?")
print(response)
# Output: 247 loans have been paid off by men.
```

Remember that at the moment, you need to make sure that the Google Sheet is public.

## Working with Polars dataframes

Example of using PandasAI with a Polars DataFrame (still in beta). In order to use Polars dataframes as a data source, you need to install the `pandasai[polars]` extra dependency.

```console
pip install pandasai[polars]
```

Then, you can use PandasAI with a Polars DataFrame as follows:

```python
from pandasai import SmartDataframe
import polars as pl

# You can instantiate a SmartDataframe with a Polars DataFrame

df = pd.DataFrame([
    "country": ["United States", "United Kingdom", "France", "Germany", "Italy", "Spain", "Canada", "Australia", "Japan", "China"],
    "gdp": [19294482071552, 2891615567872, 2411255037952, 3435817336832, 1745433788416, 1181205135360, 1607402389504, 1490967855104, 4380756541440, 14631844184064],
    "happiness_index": [6.94, 7.16, 6.66, 7.07, 6.38, 6.4, 7.23, 7.22, 5.87, 5.12]
])
df.chat("How many loans are from men and have been paid off?")
print(response)
# Output: 247 loans have been paid off by men.
```

## Plotting

Example of using PandasAI to generate a chart from a Pandas DataFrame

```python
from pandasai import SmartDataframe

df = SmartDataframe("data/Countries.csv")
response = df.chat(
    "Plot the histogram of countries showing for each the gpd, using different colors for each bar"
)
print(response)
# Output: check out images/histogram-chart.png
```

## Saving Plots with User Defined Path

You can pass a custom path to save the charts. The path must be a valid global path.
Below is the example to Save Charts with user defined location.

```python
from pandasai import SmartDataframe

user_defined_path = os.getcwd()
df = SmartDataframe("data/Countries.csv", {
    "save_charts": True,
    "save_charts_path": user_defined_path,
})
response = df.chat(
    "Plot the histogram of countries showing for each the gpd,"
    " using different colors for each bar",
)
print(response)
# Output: check out $pwd/exports/charts/{hashid}/chart.png
```

## Working with multiple dataframes (with SmartDatalake)

Example of using PandasAI with multiple dataframes. In order to use multiple dataframes as a data source, you need to use a `SmartDatalake` instead of a `SmartDataframe`. You can instantiate a `SmartDatalake` as follows:

```python
from pandasai import SmartDatalake
import pandas as pd

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

df = SmartDatalake([employees_df, salaries_df])
response = df.chat("Who gets paid the most?")
print(response)
# Output: Olivia gets paid the most.
```

## Chain of commands

You can chain commands by passing the output of one command to the next one. In the example, we first filter the original
dataframe by gender and then by loans that have been paid off.

```python
from pandasai import SmartDataframe

df = SmartDataframe("data/Loan payments data.csv")

# We filter by males only
from_males_df = df.chat("Filter the dataframe by women")

# We filter by loans that have been paid off
paid_from_males_df = from_males_df.chat("Filter the dataframe by loans that have been paid off")
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
