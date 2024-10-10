import pandasai as pai

# Load users dataset from the database
df = pai.load("my-org/users")

# Print the first 5 rows of the dataframe
print(df.head())
