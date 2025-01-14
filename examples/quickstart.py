import os
import pandasai as pai

#get your api key from https://pandabi.ai
pai.api_key.set("your api key")

#read your dataset
df = pai.read_csv("./datasets/loans_payments.csv")

#create your organization from https://pandabi.ai
df.save(path="your-organization/loans",
    name="Loans",
    description="Loans dataset")

#chat with your data
response = df.chat("what is the correlation between age and loan amount?")
print(response)

#turn the dataframe into a dashboard with chatbot for dynamic analysis
#it will appear in your organization from https://pandabi.ai
df.push()