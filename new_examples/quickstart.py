import os
import pandasai as pai

os.environ["PANDASAI_API_URL"] = "http://localhost:8000/"
os.environ["PANDASAI_API_KEY"] = "PAI-test-key"

df = pai.read_csv("/home/giuseppe/Projects/pandas-ai/examples/data/Loan payments data.csv")

# ask questions
# replace "Which are the top 5 countries by sales?" with your question
response =df.chat('How many loans are from men and have been paid off?')
print(response)

img =df.chat('Plot the chart of loans paid off by men vs by women')
print(img)

"""
#minimal save
df.save(
    path="testing/loans",
    name="loans",
    description="Loans dataset"
)
"""