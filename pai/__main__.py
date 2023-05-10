import argparse
from pandasai import PandasAI
from pandasai.llm.openai import OpenAI
from pandasai.llm.open_assistant import OpenAssistant
import pandas as pd

import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

parser = argparse.ArgumentParser(description='Pandas AI command-line tool.')
parser.add_argument('-d', '--dataset', type=str, required=True, help='The dataset to use.')
parser.add_argument('-t', '--token', type=str, required=False, default=None, help='The API token to use.')
parser.add_argument('-m', '--model', type=str, required=True, help='The type of model to use.')
parser.add_argument('-p', '--prompt', type=str, required=True, help='The prompt to use.')

def main():
    args = parser.parse_args()

    ext: str = os.path.splitext(args.dataset)[1]

    try:
        if ext == '.csv':
            df = pd.read_csv(args.dataset)
        elif ext == ".xlsx":
            df = pd.read_excel(args.dataset)
        elif ext == ".json":
            df = pd.read_json(args.dataset)
        else:
            print(f"{args.dataset} does not contain a valid file extension.")

    except:
        print(f"Could not find {args.dataset}")
        return

    if args.model == "openai":
        llm = OpenAI(api_token = args.token or os.environ.get("OPENAI_API_KEY"))

    elif args.model == "open-assistant":
        llm = OpenAssistant(api_token = args.token or os.environ.get("HUGGINGFACE_API_KEY"))

    else:
        print(f"Invalid model type: {args.model}")
        return

    try:
        pandas_ai = PandasAI(llm, verbose=True)
        response = pandas_ai.run(df, args.prompt)
        print(response)

    except:
        print("Invalid API token.")

if __name__ == '__main__':
    main()
