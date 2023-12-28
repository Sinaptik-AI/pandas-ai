# LangChain models

PandasAI has also built-in support for [LangChain](https://langchain.com/) models.

In order to use LangChain models, you need to install the `langchain` package:

```bash
pip install pandasai[langchain]
```

Once you have installed the `langchain` package, you can use it to instantiate a LangChain object:

```python
from pandasai import SmartDataframe
from langchain.llms import OpenAI

langchain_llm = OpenAI(openai_api_key="my-openai-api-key")
df = SmartDataframe("data.csv", {"llm": langchain_llm})
```

PandasAI will automatically detect that you are using a LangChain llm and will convert it to a PandasAI llm.

## More information

For more information about LangChain models, please refer to the [LangChain documentation](https://python.langchain.com/en/latest/reference/modules/llms.html).
