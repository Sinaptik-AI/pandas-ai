# Save and load dataframes

In some cases, you might want to save the configuration of a `SmartDataframe` (including the name, the description, the file path and the sample head, if any). You can do so by calling the `save` method of the `SmartDataframe` as follows:

```python
from pandasai import SmartDataframe
import pandas as pd

# head df
head_df = pd.DataFrame({
    "country": ["United States", "United Kingdom", "France", "Germany", "Italy", "Spain", "Canada", "Australia", "Japan", "China"],
    "gdp": [19294482071552, 2891615567872, 2411255037952, 3435817336832, 1745433788416, 1181205135360, 1607402389504, 1490967855104, 4380756541440, 14631844184064],
    "happiness_index": [6.94, 7.16, 6.66, 7.07, 6.38, 6.4, 7.23, 7.22, 5.87, 5.12]
})

df = SmartDataframe(
    "data/country_gdp.csv",
    name="Country GDP",
    description="A dataset containing the GDP of countries",
    custom_head=head_df
)
df.save("country")
```

From now on, you will be able to instantiate your smart dataframe without having to pass the configuration again, like this:

```python
from pandasai import SmartDataframe

df = SmartDataframe("country")
```

If you don't pass any argument to the `save` method, the name will be equals to the `name` param of the dataframe.

The configurations that you save are stored in the `pandasai.json` file, which is located in the root of your project.
