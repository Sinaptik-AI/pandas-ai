import re
import random
import string
import pandas as pd


def is_valid_email(email):
    """
    Check if the given email is valid based on regex pattern.

    :param email: str, email address to be checked
    :return: bool, True if the email is valid, otherwise False
    """
    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(email_regex, email)


def is_valid_phone_number(phone_number):
    """
    Check if the given phone number is valid based on regex pattern.

    :param phone_number: str, phone number to be checked
    :return: bool, True if the phone number is valid, otherwise False
    """
    pattern = r"\b(?:\+?\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}\b"
    return re.search(pattern, phone_number)


def is_valid_credit_card(credit_card_number):
    """
    Check if the given credit card number is valid based on regex pattern.

    :param credit_card_number: str, credit card number to be checked
    :return: bool, True if the credit card number is valid, otherwise False
    """
    pattern = r"^\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}$"
    return re.search(pattern, credit_card_number)


def generate_random_email():
    """
    Generate a random email address using predefined domains.

    :return: str, generated random email address
    """
    domains = [
        "gmail.com",
        "yahoo.com",
        "hotmail.com",
        "outlook.com",
        "icloud.com",
        "aol.com",
        "protonmail.com",
        "zoho.com",
    ]
    name_length = random.randint(6, 12)
    domain = random.choice(domains)
    letters = string.ascii_lowercase + string.digits + "-_"
    username = "".join(random.choice(letters) for i in range(name_length))
    email = username + "@" + domain
    return email


def generate_random_phone_number():
    """
    Generate a random phone number with country code.

    :return: str, generated random phone number
    """
    area_code = str(random.randint(0, 99))
    number = "".join(random.choices("0123456789", k=10))
    phone_number = f"+{area_code} {number}"
    return phone_number


def generate_random_credit_card():
    """
    Generate a random credit card number.

    :return: str, generated random credit card number
    """
    groups = []
    for i in range(4):
        group = "".join(random.choices("0123456789", k=4))
        groups.append(group)
    separator = random.choice(["-", " "])
    return separator.join(groups)


def copy_head(df: pd.DataFrame):
    """
    Copy the head of a DataFrame.

    :param df: pd.DataFrame, the DataFrame to copy the head from
    :return: pd.DataFrame, copied head of the DataFrame
    """ 
    return df.head().copy()


def anonymize_dataframe_head(data_frame: pd.DataFrame):
    """
    Anonymize the head of a given DataFrame by replacing sensitive data.

    :param data_frame: pd.DataFrame, the DataFrame to anonymize the head
    :return: pd.DataFrame, anonymized head of the DataFrame
    """
    df = copy_head(data_frame)
    for col in df.columns:
        col_idx = df.columns.get_loc(col)
        for row_idx, val in enumerate(df[col]):
            cell_value = str(val)

            if is_valid_email(cell_value):
                df.iloc[row_idx, col_idx] = generate_random_email()
                continue
            if is_valid_phone_number(cell_value):
                df.iloc[row_idx, col_idx] = generate_random_phone_number()
                continue
            if is_valid_credit_card(cell_value):
                df.iloc[row_idx, col_idx] = generate_random_credit_card()
                continue

            # anonymize data
            random_row_index = random.choice(
                [i for i in range(len(df.index)) if i != row_idx]
            )
            random_value = df.iloc[random_row_index, col_idx]
            df.iloc[row_idx, col_idx] = random_value
            df.iloc[random_row_index, col_idx] = cell_value
    return df
