# Command-Line Tool
[Pai] is the command line tool designed to provide a convenient way to interact with `pandasai` through a command line interface (CLI). In order to access the CLI tool, make sure to create a virtualenv for testing purpose and to install project dependencies in your local virtual environment using `pip` by running the following command:
```
pip install -e .
```
Alternatively, you can use `poetry` to create and activate the virtual environment by running the following command:
```
poetry shell
```
Inside the activated virtual environment, install the project dependencies by running the following command:
```
poetry install
```

By following these steps, you will now have the necessary environment to access the CLI tool. 

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
>For example,
>```
>pai -d "~/pandasai/example/data/Loan payments data.csv" -m "openai" -p "How many loans are from men and have been paid off?"
>```
>Should result in the same output as the `from_csv.py` example.
