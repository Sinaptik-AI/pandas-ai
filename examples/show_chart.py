import pandas as pd
from data.sample_dataframe import dataframe
from pandasai import PandasAI
from pandasai.llm.openai import OpenAI

def main():
    # Load data into a DataFrame
    df = pd.DataFrame(dataframe)

    # Initialize PandasAI with OpenAI's language model
    llm = OpenAI()
    pandas_ai = PandasAI(llm)

    # Generate a chart based on the user's query
    query = "Plot the histogram of countries showing for each the gpd, using different colors for each bar"
    response = pandas_ai.run(df, query)

    # Display the chart to the user
    print(response)
    # Output: check out images/histogram-chart.png

if __name__ == "__main__":
    main()

