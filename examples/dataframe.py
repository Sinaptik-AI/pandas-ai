import os

import pandasai as pai

# Create a sample pandas DataFrame
data = {
    "Name": ["John", "Emma", "Liam", "Olivia", "Noah"],
    "Age": [28, 35, 22, 31, 40],
    "City": ["New York", "London", "Paris", "Tokyo", "Sydney"],
    "Salary": [75000, 82000, 60000, 79000, 88000],
}

# Create a DataFrame
df = pai.DataFrame(data)

# By default, unless you choose a different LLM, it will use BambooLLM.
# You can get your free API key signing up at https://pandabi.ai (you can also configure it in your .env file)
os.environ["PANDASAI_API_KEY"] = "YOUR_API_KEY"

# Chat with the DataFrame
answer = df.chat("Who has the highest salary?")
print(f"Answer: {answer}")

# Follow up question
follow_up_answer = df.follow_up("What is their age?")
print(f"Follow-up answer: {follow_up_answer}")

# Another follow-up question
another_follow_up = df.follow_up("How many people are younger than this person?")
print(f"Another follow-up answer: {another_follow_up}")
