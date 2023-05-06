"""
This module contains helper functions for anonymizing data and generating random data
before sending it to the LLM.
"""

import random
import re
import string

import pandas as pd


def is_valid_email(email: str) -> bool:
    """
    Check if the given email is valid based on regex pattern.

    :param email: str, email address to be checked
    :return: bool, True if the email is valid, otherwise False
    """
    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(email_regex, email) is not None


def is_valid_phone_number(phone_number: str) -> bool:
    """
    Check if the given phone number is valid based on regex pattern.

    :param phone_number: str, phone number to be checked
    :return: bool, True if the phone number is valid, otherwise False
    """
    pattern = r"\b(?:\+?\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}\b"
    return re.search(pattern, phone_number) is not None


def is_valid_credit_card(credit_card_number: str) -> bool:
    """
    Check if the given credit card number is valid based on regex pattern.

    :param credit_card_number: str, credit card number to be checked
    :return: bool, True if the credit card number is valid, otherwise False
    """
    pattern = r"^\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}$"
    return re.search(pattern, credit_card_number) is not None


def generate_random_email() -> str:
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


def generate_random_phone_number(original_field: str) -> str:
    """
    Generate a random phone number with country code if originally present.

    :param original_field: str, original phone number field
    :return: str, generated random phone number
    """
    if original_field.startswith("+"):
        # Extract country code if present
        country_code = original_field.split()[0]
    else:
        country_code = ""

    number = "".join(random.choices("0123456789", k=10))

    if country_code:
        phone_number = f"{country_code} {number}"
    else:
        phone_number = number

    return phone_number


def generate_random_credit_card() -> str:
    """
    Generate a random credit card number.

    :return: str, generated random credit card number
    """
    groups = []
    for _i in range(4):
        group = "".join(random.choices("0123456789", k=4))
        groups.append(group)
    separator = random.choice(["-", " "])
    return separator.join(groups)


def copy_head(data_frame: pd.DataFrame) -> pd.DataFrame:
    """
    Copy the head of a DataFrame.

    :param data_frame: pd.DataFrame, the DataFrame to copy the head from
    :return: pd.DataFrame, copied head of the DataFrame
    """
    return data_frame.head().copy()


def anonymize_dataframe_head(data_frame: pd.DataFrame) -> pd.DataFrame:
    """
    Anonymize the head of a given DataFrame by replacing sensitive data.

    :param data_frame: pd.DataFrame, the DataFrame to anonymize the head
    :return: pd.DataFrame, anonymized head of the DataFrame
    """
    data_frame = copy_head(data_frame)
    for col in data_frame.columns:
        col_idx = data_frame.columns.get_loc(col)
        for row_idx, val in enumerate(data_frame[col]):
            cell_value = str(val)

            if is_valid_email(cell_value):
                data_frame.iloc[row_idx, col_idx] = generate_random_email()
                continue
            if is_valid_phone_number(cell_value):
                data_frame.iloc[row_idx, col_idx] = generate_random_phone_number(
                    cell_value
                )
                continue
            if is_valid_credit_card(cell_value):
                data_frame.iloc[row_idx, col_idx] = generate_random_credit_card()
                continue

            # anonymize data
            random_row_index = random.choice(
                [i for i in range(len(data_frame.index)) if i != row_idx]
            )
            random_value = data_frame.iloc[random_row_index, col_idx]
            data_frame.iloc[row_idx, col_idx] = random_value
            data_frame.iloc[random_row_index, col_idx] = cell_value
    return data_frame
