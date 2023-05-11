# Import required modules
import pandas as pd
from pandasai import PandasAI
from pandasai.llm.openai import OpenAI

# Load data from CSV file
loan_data = pd.read_csv("data/Loan payments data.csv")

# Initialize PandasAI object with OpenAI language model
llm = OpenAI()
pandas_ai = PandasAI(llm, verbose=True)

# Run PandasAI query on loan data
query = "How many loans are from men and have been paid off?"
response = pandas_ai.run(loan_data, query)

# Print response message
num_loans = response['answer']
message = f"{num_loans} loans have been paid off by men."
print(message)
