import argparse
from pandasai import PandasAI
from pandasai.llm.openai import OpenAI
from pandasai.llm.open_assistant import OpenAssistant
import pandas as pd

import os
from dotenv import load_dotenv

load_dotenv()

parser = argparse.ArgumentParser(description='Pandas AI command-line tool.')
parser.add_argument('-d', '--dataset', type=str, required=True, help='The dataset to use.')
parser.add_argument('-m', '--model', type=str, required=True, help='The type of model to use.')
parser.add_argument('-p', '--prompt', type=str, required=True, help='The prompt to use.')

def main():
    args = parser.parse_args()

    try:
        df = pd.read_csv(args.dataset)
    except:
        raise ValueError(f"Could not find {args.dataset}")

    if args.model == "openai":
        llm = OpenAI(api_token = os.environ.get("OPENAI_API_KEY"))

    elif args.model == "open-assistant":
        llm = OpenAssistant(api_token = os.environ.get("HUGGINGFACE_API_KEY"))

    else:
        raise ValueError(f"Invalid model type: {args.model}")

    try:
        pandas_ai = PandasAI(llm, verbose=True)
        response = pandas_ai.run(df, args.prompt)
        print(response)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    main()
