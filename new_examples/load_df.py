import os
import pandasai as pai

os.environ["PANDASAI_API_URL"] = "http://localhost:8000/"
os.environ["PANDASAI_API_KEY"] = "PAI-test-key"

# Load using organization/dataset format
#df = pai.load("/home/giuseppe/Projects/pandas-ai/datasets/testing/loans")
df = pai.load("/home/giuseppe/Projects/pandas-ai/datasets/testing/loans", virtualized=True)

print(df.head())