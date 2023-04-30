# PandasAI 🐼

Pandas AI is a Python library that adds generative artificial intelligence capabilities to Pandas, the popular data analysis and manipulation tool. It is designed to be used in conjunction with Pandas, and is not a replacement for it.

<!-- Add images/pandas-ai.png -->

![PandasAI](images/pandas-ai.png?raw=true)

## Demo

Try out PandasAI in your browser from on [Google Colab](https://colab.research.google.com/drive/1rKz7TudOeCeKGHekw7JFNL4sagN9hon-?usp=sharing).

## Installation

```bash
pip install pandasai
```

## Usage

PandasAI is designed to be used in conjunction with Pandas. It makes Pandas conversational, allowing you to ask questions about your data and get answers back, in the form of Pandas DataFrames. For example, you can ask PandasAI to find all the rows in a DataFrame where the value of a column is greater than 5, and it will return a DataFrame containing only those rows:

```python
import pandas as pd
from pandasai import PandasAI

# Sample DataFrame
df = pd.DataFrame({
    "country": ["United States", "United Kingdom", "France", "Germany", "Italy", "Spain", "Canada", "Australia", "Japan", "China"],
    "gdp": [21400000, 2940000, 2830000, 3870000, 2160000, 1350000, 1780000, 1320000, 516000, 14000000],
    "happiness_index": [7.3, 7.2, 6.5, 7.0, 6.0, 6.3, 7.3, 7.3, 5.9, 5.0]
})

# Instantiate a LLM
from pandasai.llm.openai import OpenAI
llm = OpenAI()

pandas_ai = PandasAI(llm)
pandas_ai.run(df, prompt='Which are the 5 happiest countries?')
```

The above code will return the following:

```
0     United States
6            Canada
7         Australia
1    United Kingdom
3           Germany
Name: country, dtype: object
```

Of course, you can also ask PandasAI to perform more complex queries. For example, you can ask PandasAI to find the sum of the GDPs of the 2 unhappiest countries:

```python
pandas_ai.run(df, prompt='What is the sum of the GDPs of the 2 unhappiest countries?')
```

The above code will return the following:

```
14516000
```

You can find more examples in the [examples](examples) directory.

## Environment Variables

In order to set the API key for the LLM (Hugging Face Hub, OpenAI), you need to set the appropriate environment variables. You can do this by copying the `.env.example` file to `.env`:

```bash
cp .env.example .env
```

Then, edit the `.env` file and set the appropriate values.

As an alternative, you can also pass the environment variables directly to the constructor of the LLM:

```python
# OpenAI
llm = OpenAI(api_token="YOUR_OPENAI_API_KEY")

# OpenAssistant
llm = OpenAssistant(api_token="YOUR_HF_API_KEY")
```

## License

PandasAI is licensed under the MIT License. See the LICENSE file for more details.

## Contributing

Contributions are welcome! Please check out the todos below, and feel free to open a pull request.

### Todo

- [ ] Add support for more LLMs
- [ ] Make PandasAI available from a CLI
- [ ] Create a web interface for PandasAI
- [ ] Add unit tests
- [ ] Add contributing guidelines
- [x] Add CI
- [x] Add support for conversational responses
