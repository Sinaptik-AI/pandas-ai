import pandas as pd
from pandasai import PandasAI
from pandasai.llm.openai import OpenAI

df = pd.DataFrame({
    "country": ["United States", "United Kingdom", "France", "Germany", "Italy", "Spain", "Canada", "Australia", "Japan", "China"],
    "gdp": [21400000, 2940000, 2830000, 3870000, 2160000, 1350000, 1780000, 1320000, 516000, 14000000],
    "happiness_index": [7.3, 7.2, 6.5, 7.0, 6.0, 6.3, 7.3, 7.3, 5.9, 5.0]
})

llm = OpenAI()
pandas_ai = PandasAI(llm, verbose = True)
response = pandas_ai.run(df, "Calculate the sum of the gdp of north american countries")
print(response)