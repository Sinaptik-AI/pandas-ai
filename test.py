from pandasai.callbacks.base import StdoutCallBack, BaseCallback
from pandasai import PandasAI
from pandasai.llm.openai import OpenAI
import pandas as pd

llm = OpenAI(api_token="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")

df = pd.DataFrame({
    "country": ["United States", "United Kingdom", "France", "Germany", "Italy", "Spain", "Canada", "Australia", "Japan", "China"],
    "gdp": [19294482071552, 2891615567872, 2411255037952, 3435817336832, 1745433788416, 1181205135360, 1607402389504, 1490967855104, 4380756541440, 14631844184064],
    "happiness_index": [6.94, 7.16, 6.66, 7.07, 6.38, 6.4, 7.23, 7.22, 5.87, 5.12]
})

class MyCustomCallback(BaseCallback):
    def on_code(self, response: str):
        print("My custom call back")
        print(response)

m = MyCustomCallback()
p = PandasAI(llm=llm, callback=m)

print(p.run(df,prompt="give me max gdp"))
