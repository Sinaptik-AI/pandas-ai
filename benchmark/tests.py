tests = [
    {
        "input": "How many missing values and duplicates are in the customer information dataset?",
        "expected_output": """missing_values_customer_info = dfs[0].isnull().sum().sum()
duplicates_customer_info = customer_info.duplicated().sum()
result = {'type': 'string', 'value': f'Missing values: {missing_values}, Duplicates: {duplicates}'}""",
        "datasets": "benchmark/data/customer_info.csv",
    },
    {
        "input": "Can you provide the customer information dataset without any missing values and duplicates?",
        "expected_output": """customer_info_clean = dfs[0].dropna().drop_duplicates()
result = {'type': 'dataframe', 'value': customer_info_clean}""",
        "datasets": "benchmark/data/customer_info.csv",
    },
    {
        "input": "What are the mean, median, and standard deviation of the tenure (in months) of customers?",
        "expected_output": """mean_tenure = dfs[0]['tenure'].mean()
median_tenure = dfs[0]['tenure'].median()
std_dev_tenure = dfs[0]['tenure'].std()
result = {'type': 'string', 'value': f'Mean: {mean_tenure}, Median: {median_tenure}, Standard Deviation: {std_dev_tenure}'}""",
        "datasets": "benchmark/data/customer_info.csv",
    },
    {
        "input": "What is the distribution of gender among customers?",
        "expected_output": """gender_distribution = dfs[0]['gender'].value_counts()
result = {'type': 'dataframe', 'value': gender_distribution}""",
        "datasets": "benchmark/data/customer_info.csv",
    },
    {
        "input": "What percentage of customers churned in the past 12 months?",
        "expected_output": """churn_rate = dfs[0]['Churn'].value_counts(normalize=True) * 100
result = {'type': 'dataframe', 'value': churn_rate}""",
        "datasets": "benchmark/data/customer_info.csv",
    },
    {
        "input": "Can you provide the correlation matrix of the services?",
        "expected_output": """correlation_matrix = dfs[0].corr()
result = {'type': 'dataframe', 'value': correlation_matrix}""",
        "datasets": "benchmark/data/service_info.csv",
    },
    {
        "input": "What is the distribution of different types of internet services subscribed to by customers?",
        "expected_output": """internet_service_distribution = dfs[0]['InternetService'].value_counts()
result = {'type': 'dataframe', 'value': internet_service_distribution}""",
        "datasets": "benchmark/data/service_info.csv",
    },
    {
        "input": "What are the earliest and latest service start dates recorded in the dataset?",
        "expected_output": """earliest_start_date = dfs[0]['ServiceStartDate'].min()
latest_start_date = dfs[0]['ServiceStartDate'].max()
result = {'type': 'string', 'value': f'Earliest Start Date: {earliest_start_date}, Latest Start Date: {latest_start_date}'}""",
        "datasets": "benchmark/data/service_info.csv",
    },
    {
        "input": "How many customers have unlimited and limited data caps?",
        "expected_output": """data_caps = dfs[0]['DataCap'].value_counts()
result = {'type': 'dataframe', 'value': data_caps}""",
        "datasets": "benchmark/data/service_info.csv",
    },
    {
        "input": "Which router models are most commonly used by customers?",
        "expected_output": """router_model_distribution = dfs[0]['RouterModel'].value_counts()
result = {'type': 'dataframe', 'value': router_model_distribution}""",
        "datasets": "benchmark/data/service_info.csv",
    },
    {
        "input": "What is the total revenue generated based on the billing information?",
        "expected_output": """total_revenue = dfs[0]['TotalCharges'].sum()
result = {'type': 'number', 'value': total_revenue}""",
        "datasets": "benchmark/data/billing_info.csv",
    },
    {
        "input": "How are payments distributed among different methods (Electronic check, Mailed check, Bank transfer, Credit card)?",
        "expected_output": """payment_distribution = dfs[0]['PaymentMethod'].value_counts()
result = {'type': 'dataframe', 'value': payment_distribution}""",
        "datasets": "benchmark/data/billing_info.csv",
    },
    {
        "input": "What is the average number of late payments made by customers?",
        "expected_output": """average_late_payments = dfs[0]['LatePayments'].mean()
result = {'type': 'number', 'value': average_late_payments}""",
        "datasets": "benchmark/data/billing_info.csv",
    },
    {
        "input": "What are the common patterns observed in payment histories?",
        "expected_output": """payment_history_patterns = dfs[0]['PaymentHistory'].value_counts()
result = {'type': 'dataframe', 'value': payment_history_patterns}""",
        "datasets": "benchmark/data/billing_info.csv",
    },
    {
        "input": "How many customers prefer paperless billing compared to traditional billing?",
        "expected_output": """billing_preference = dfs[0]['PaperlessBilling'].value_counts()
result = {'type': 'dataframe', 'value': billing_preference}""",
        "datasets": "benchmark/data/billing_info.csv",
    },
    {
        "input": "What is the total revenue generated from residential and business services?",
        "expected_output": """billing_info = dfs[0]
service_info = dfs[1]
merged_data = billing_info.merge(service_info, on='customerID')
revenue_by_service_type = merged_data.groupby('ServiceType')['TotalCharges'].sum()
result = {'type': 'dataframe', 'value': revenue_by_service_type}""",
        "datasets": [
            "benchmark/data/billing_info.csv",
            "benchmark/data/service_info.csv",
        ],
    },
    {
        "input": "How is the distribution of residential and business services among male and female customers?",
        "expected_output": """customer_info = dfs[0]
service_info = dfs[1]
merged_data = billing_info.merge(service_info, on='customerID')
service_type_distribution_by_gender = merged_data.groupby(['gender', 'ServiceType']).size()
result = {'type': 'dataframe', 'value': service_type_distribution}""",
        "datasets": [
            "benchmark/data/customer_info.csv",
            "benchmark/data/service_info.csv",
        ],
    },
    {
        "input": "What is the average contract value across different education levels?",
        "expected_output": """customer_info = dfs[0]
billing_info = dfs[1]
merged_data = customer_info.merge(billing_info, on='customerID')
average_contract_value_by_education = merged_data.groupby('Education')['TotalCharges'].mean()
result = {'type': 'dataframe', 'value': average_contract_value_by_education}""",
        "datasets": [
            "benchmark/data/customer_info.csv",
            "benchmark/data/billing_info.csv",
        ],
    },
    {
        "input": "How much revenue is lost due to customer churn?",
        "expected_output": """customer_info = dfs[0]
billing_info = dfs[1]
churned_customers = customer_info.merge(billing_info, on='customerID')
churned_customers = churned_customers[churned_customers['Churn'] == 'Yes']
revenue_lost_due_to_churn = churned_customers['MonthlyCharges'].sum()
result = {'type': 'number', 'value': revenue_lost_due_to_churn}""",
        "datasets": [
            "benchmark/data/customer_info.csv",
            "benchmark/data/billing_info.csv",
        ],
    },
    {
        "input": "How many customers use DSL and Fiber optic internet services across different education levels?",
        "expected_output": """customer_info = dfs[0]
service_info = dfs[1]
merged_data = customer_info.merge(service_info, on='customerID')
sales_count_by_internet_service_education = merged_data.groupby(['InternetService', 'Education']).size()

result = { "type": "dataframe", "value": sales_count_by_internet_service_education.to_frame('count') }""",
        "datasets": [
            "benchmark/data/customer_info.csv",
            "benchmark/data/service_info.csv",
        ],
    },
]
