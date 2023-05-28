""" Driver code for the CLI tool
Pai is the command line tool designed to provide a convenient way to interact with PandasAI
through a command line interface (CLI).

```
pai [OPTIONS]
```
Options:

- **-d, --dataset**: The file path to the dataset.
- **-t, --token**: Your HuggingFace or OpenAI API token, if no token provided pai will pull
from the `.env` file.
- **-m, --model**: Choice of LLM, either `openai`, `open-assistant`, or `starcoder`.
- **-p, --prompt**: Prompt that PandasAI will run.

To view a full list of available options and their descriptions, run the following command:

```
pai --help

```

Example:
    ```
    pai -d "~/pandasai/example/data/Loan payments data.csv" -m "openai"
    -p "How many loans are from men and have been paid off?"

    ```

> Should result in the same output as the `from_csv.py` example.

"""
import os
import click
import pandas as pd
from pandasai import PandasAI
from pandasai.llm.openai import OpenAI
from pandasai.llm.open_assistant import OpenAssistant
from pandasai.llm.starcoder import Starcoder
from pandasai.llm.google_palm import GooglePalm

@click.command()
@click.option('-d', '--dataset', type=str, required=True, help='The dataset to use.')
@click.option('-t', '--token', type=str, required=False, default=None, help='The API token to use.')
@click.option('-m', '--model', type=click.Choice(['openai', 'open-assistant', 'starcoder', 'palm']),
              required=True, help='The type of model to use.')
@click.option('-p', '--prompt', type=str, required=True, help='The prompt to use.')
def main(dataset: str, token: str, model: str, prompt: str) -> None:
    """Main logic for the command line interface tool."""

    ext = os.path.splitext(dataset)[1]

    try:
        file_format = {
            ".csv": pd.read_csv,
            ".xls": pd.read_excel,
            ".xlsx": pd.read_excel,
            ".xlsm": pd.read_excel,
            ".xlsb": pd.read_excel,
            ".json": pd.read_json,
            ".html": pd.read_html,
            ".sql": pd.read_sql,
            ".feather": pd.read_feather,
            ".parquet": pd.read_parquet,
            ".dta": pd.read_stata,
            ".sas7bdat": pd.read_sas,
            ".h5": pd.read_hdf,
            ".hdf5": pd.read_hdf,
            ".pkl": pd.read_pickle,
            ".pickle": pd.read_pickle,
            ".gbq": pd.read_gbq,
            ".orc": pd.read_orc,
            ".xpt": pd.read_sas,
            ".sav": pd.read_spss,
            ".gz": pd.read_csv,
            ".zip": pd.read_csv,
            ".bz2": pd.read_csv,
            ".xz": pd.read_csv,
            ".txt": pd.read_csv,
            ".xml": pd.read_xml,
        }
        if ext in file_format:
            df = file_format[ext](dataset) # pylint: disable=C0103
        else:
            print("Unsupported file format.")
            return

    except Exception as e: # pylint: disable=W0718 disable=C0103
        print(e)
        return

    if model == "openai":
        llm = OpenAI(api_token = token)

    elif model == "open-assistant":
        llm = OpenAssistant(api_token = token)

    elif model == 'starcoder':
        llm = Starcoder(api_token = token)

    elif model == 'palm':
        llm = GooglePalm(api_key = token)

    try:
        pandas_ai = PandasAI(llm, verbose=True)
        response = pandas_ai(df, prompt)
        print(response)

    except Exception as e: # pylint: disable=W0718 disable=C0103
        print(e)
