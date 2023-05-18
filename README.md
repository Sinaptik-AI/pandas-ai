# PandasAI 🐼

[![release](https://img.shields.io/pypi/v/pandasai?label=Release&style=flat-square)](https://pypi.org/project/pandasai/)
[![lint](https://github.com/gventuri/pandas-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/gventuri/pandas-ai/actions/workflows/ci.yml/badge.svg)
[![lint](https://github.com/gventuri/pandas-ai/actions/workflows/cd.yml/badge.svg)](https://github.com/gventuri/pandas-ai/actions/workflows/cd.yml/badge.svg)
[![](https://dcbadge.vercel.app/api/server/kF7FqH2FwS?style=flat&compact=true)](https://discord.gg/kF7FqH2FwS)
[![Downloads](https://static.pepy.tech/badge/pandasai/month)](https://pepy.tech/project/pandasai) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Open in Colab](https://camo.githubusercontent.com/84f0493939e0c4de4e6dbe113251b4bfb5353e57134ffd9fcab6b8714514d4d1/68747470733a2f2f636f6c61622e72657365617263682e676f6f676c652e636f6d2f6173736574732f636f6c61622d62616467652e737667)](https://colab.research.google.com/drive/1rKz7TudOeCeKGHekw7JFNL4sagN9hon-?usp=sharing)

Pandas AI is a Python library that adds generative artificial intelligence capabilities to Pandas, the popular data analysis and manipulation tool. It is designed to be used in conjunction with Pandas, and is not a replacement for it.

<!-- Add images/pandas-ai.png -->

![PandasAI](images/pandas-ai.png?raw=true)

## Demo

Try out PandasAI in your browser:

[![Open in Colab](https://camo.githubusercontent.com/84f0493939e0c4de4e6dbe113251b4bfb5353e57134ffd9fcab6b8714514d4d1/68747470733a2f2f636f6c61622e72657365617263682e676f6f676c652e636f6d2f6173736574732f636f6c61622d62616467652e737667)](https://colab.research.google.com/drive/1rKz7TudOeCeKGHekw7JFNL4sagN9hon-?usp=sharing)

## Installation

```bash
pip install pandasai
```

## Usage

> Disclaimer: GDP data was collected from [this source](https://ourworldindata.org/grapher/gross-domestic-product?tab=table), published by World Development Indicators - World Bank (2022.05.26) and collected at National accounts data - World Bank / OECD. It relates to the year of 2020. Happiness indexes were extracted from [the World Happiness Report](https://ftnnews.com/images/stories/documents/2020/WHR20.pdf). Another useful [link](https://data.world/makeovermonday/2020w19-world-happiness-report-2020).

PandasAI is designed to be used in conjunction with [pandas](https://github.com/pandas-dev/pandas). It makes Pandas conversational, allowing you to ask questions about your data and get answers back, in the form of pandas DataFrames. For example, you can ask PandasAI to find all the rows in a DataFrame where the value of a column is greater than 5, and it will return a DataFrame containing only those rows:

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
pandas_ai(df, prompt='Which are the 5 happiest countries?')
```

The above code will return the following:

```
6            Canada
7         Australia
1    United Kingdom
3           Germany
0     United States
Name: country, dtype: object
```

Of course, you can also ask PandasAI to perform more complex queries. For example, you can ask PandasAI to find the sum of the GDPs of the 2 unhappiest countries:

```python
pandas_ai(df, prompt='What is the sum of the GDPs of the 2 unhappiest countries?')
```

The above code will return the following:

```
19012600725504
```

You can also ask PandasAI to draw a graph:

```python
pandas_ai(
    df,
    "Plot the histogram of countries showing for each the gpd, using different colors for each bar",
)
```

![Chart](images/histogram-chart.png?raw=true)

You can find more examples in the [examples](examples) directory.

## Command-Line Tool

Pai is the command line tool designed to provide a convenient way to interact with PandasAI through a command line interface (CLI).

```
pai [OPTIONS]
```

Options:

- **-d, --dataset**: The file path to the dataset.
- **-t, --token**: Your HuggingFace or OpenAI API token, if no token provided pai will pull from the `.env` file.
- **-m, --model**: Choice of LLM, either `openai`, `open-assistant`, or `starcoder`.
- **-p, --prompt**: Prompt that PandasAI will run.

To view a full list of available options and their descriptions, run the following command:

```
pai --help

```

> For example,
>
> ```
> pai -d "~/pandasai/example/data/Loan payments data.csv" -m "openai" -p "How many loans are from men and have been paid off?"
> ```
>
> Should result in the same output as the `from_csv.py` example.

## Privacy & Security

In order to generate the Python code to run, we take the dataframe head, we randomize it (using random generation for sensitive data and shuffling for non-sensitive data) and send just the head.

Also, if you want to enforce further your privacy you can instantiate PandasAI with `enforce_privacy = True` which will not send the head (but just column names) to the LLM.

## Environment Variables

In order to set the API key for the LLM (Hugging Face Hub, OpenAI), you need to set the appropriate environment variables. You can do this by copying the `.env.example` file to `.env`:

```bash
cp .env.example .env
```

Then, edit the `.env` file and set the appropriate values.

As an alternative, you can also pass the environment variables directly to the constructor of the LLM:

```python
# OpenAI
llm = OpenAI(api_token="YOUR_API_KEY")

# Starcoder
llm = Starcoder(api_token="YOUR_HF_API_KEY")
```

## License

PandasAI is licensed under the MIT License. See the LICENSE file for more details.

## Contributing

Contributions are welcome! Please check out the todos below, and feel free to open a pull request.
For more information, please see the [contributing guidelines](CONTRIBUTING.md).

After installing the virtual environment, please remember to install `pre-commit` to be compliant with our standards:

```bash
pre-commit install
```

## Acknowledgements

- This project is based on the [pandas](https://github.com/pandas-dev/pandas) library by independent contributors, but it's in no way affiliated with the pandas project.
- This project is meant to be used as a tool for data exploration and analysis, and it's not meant to be used for production purposes. Please use it responsibly.

### Todo

- [ ] Add support for more LLMs
- [x] Make PandasAI available from a CLI
- [ ] Create a web interface for PandasAI
- [ ] Add unit tests
- [x] Add contributing guidelines
- [x] Add CI
- [x] Add support for conversational responses
