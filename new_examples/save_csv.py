import os
import pandasai as pai

os.environ["PANDASAI_API_URL"] = "http://localhost:8000/"
os.environ["PANDASAI_API_KEY"] = "PAI-test-key"

df = pai.read_csv("/home/giuseppe/Projects/pandas-ai/examples/data/Loan payments data.csv")

#save with fields descriptions
df.save(
    path="testing/loans",
    name="loans",
    description="Loans dataset",
    columns=[
        {
            "name": "Loan_ID",
            "type": "string",
            "description": "Unique identifier for each loan"
        },
        {
            "name": "loan_status",
            "type": "string",
            "description": "Status of the loan (PAIDOFF, COLLECTION, COLLECTION_PAIDOFF)"
        },
        {
            "name": "Principal",
            "type": "number",
            "description": "The initial amount of the loan"
        },
        {
            "name": "terms",
            "type": "number",
            "description": "The duration of the loan in days"
        },
        {
            "name": "effective_date",
            "type": "date",
            "description": "The date when the loan became effective"
        },
        {
            "name": "due_date",
            "type": "date",
            "description": "The date when the loan payment is due"
        },
        {
            "name": "paid_off_time",
            "type": "datetime",
            "description": "The timestamp when the loan was paid off (if applicable)"
        },
        {
            "name": "past_due_days",
            "type": "number",
            "description": "Number of days the payment is past due (if applicable)"
        },
        {
            "name": "age",
            "type": "number",
            "description": "Age of the borrower"
        },
        {
            "name": "education",
            "type": "string",
            "description": "Education level of the borrower (High School or Below, Bachelor, college, Master or Above)"
        },
        {
            "name": "Gender",
            "type": "string",
            "description": "Gender of the borrower (male/female)"
        }
    ]
)