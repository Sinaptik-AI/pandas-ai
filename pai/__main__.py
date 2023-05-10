import argparse
from pandasai import PandasAI
from pandasai.llm.openai import OpenAI
from pandasai.llm.open_assistant import OpenAssistant
from pandasai.llm.starcoder import Starcoder
import pandas as pd

parser = argparse.ArgumentParser(description='Process some command-line arguments.')
parser.add_argument('-d', '--dataset', type=str, required=True, help='The dataset to use.')
parser.add_argument('-m', '--model', type=str, required=True, help='The type of model to use.')
parser.add_argument('-t', '--token', type=str, required=True, help='The API token to use.')
parser.add_argument('-p', '--prompt', type=str, required=True, help='The prompt to use.')

def main():
    args = parser.parse_args()

    try:
        df = pd.read_csv(args.dataset)

    except:
        raise ValueError("Couldn't find dataset")

    if args.model == "openai":
        llm = OpenAI(api_token=args.token)

    elif args.model == "open-assistant":
        llm = OpenAssistant(api_token=args.token)

    elif args.model == "starcoder":
        llm = Starcoder(api_token=args.token)

    else:
        raise ValueError("Incorrect Model Type")

    pandas_ai = PandasAI(llm, verbose=True)
    response = pandas_ai.run(df, args.prompt)
    print(response)

if __name__ == '__main__':
    main()
