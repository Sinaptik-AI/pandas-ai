import os
from dotenv import load_dotenv
import click
import pandas as pd
from pandasai import PandasAI
from pandasai.llm.openai import OpenAI
from pandasai.llm.open_assistant import OpenAssistant

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

@click.command()
@click.option('-d', '--dataset', type=str, required=True, help='The dataset to use.')
@click.option('-t', '--token', type=str, required=False, default=None, help='The API token to use.')
@click.option('-m', '--model', type=click.Choice(['openai', 'open-assistant']), required=True, help='The type of model to use.')
@click.option('-p', '--prompt', type=str, required=True, help='The prompt to use.')
def main(dataset, token, model, prompt):
    ext = os.path.splitext(dataset)[1]

    try:
        if ext == '.csv':
            df = pd.read_csv(dataset)
        elif ext == ".xlsx":
            df = pd.read_excel(dataset)
        elif ext == ".json":
            df = pd.read_json(dataset)
        else:
            print(f"{dataset} does not contain a valid file extension.")
            return

    except:
        print(f"Could not find {dataset}")
        return

    if model == "openai":
        llm = OpenAI(api_token = token or os.environ.get("OPENAI_API_KEY"))

    elif model == "open-assistant":
        llm = OpenAssistant(api_token = token or os.environ.get("HUGGINGFACE_API_KEY"))

    try:
        pandas_ai = PandasAI(llm, verbose=True)
        response = pandas_ai.run(df, prompt)
        print(response)

    except:
        print("Invalid API token.")

if __name__ == '__main__':
    main()
