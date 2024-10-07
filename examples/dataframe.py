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

# Chat with the DataFrame
answer = df.chat("Who has the highest salary?")
print(f"Answer: {answer}")
