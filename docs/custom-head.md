# Use custom head

In some cases, you might want to share a custom sample head to the LLM. For example, you might not be willing to share potential sensitive information with the LLM. Or you might just want to provide better examples to the LLM to improve the quality of the answers. You can do so by passing a custom head to the LLM as follows:

```python
from pandasai import SmartDataframe
import pandas as pd

# head df
head_df = pd.DataFrame({
    "country": ["United States", "United Kingdom", "France", "Germany", "Italy", "Spain", "Canada", "Australia", "Japan", "China"],
    "gdp": [19294482071552, 2891615567872, 2411255037952, 3435817336832, 1745433788416, 1181205135360, 1607402389504, 1490967855104, 4380756541440, 14631844184064],
    "happiness_index": [6.94, 7.16, 6.66, 7.07, 6.38, 6.4, 7.23, 7.22, 5.87, 5.12]
})

df = SmartDataframe("data/country_gdp.csv", {
    "sample_head": head_df
})
```

Doing so will make the LLM use the `head_df` as the sample head instead of the first 5 rows of the dataframe.
