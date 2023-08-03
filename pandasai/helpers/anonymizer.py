"""
Helper class to anonymize a dataframe head by replacing the values of the columns
that contain personal or sensitive information with random values.
"""

import random
import re
import string

import pandas as pd


class Anonymizer:
    def _is_valid_email(email: str) -> bool:
        """Check if the given email is valid based on regex pattern.

        Args:
            email (str): email address to be checked.

        Returns (bool): True if the email is valid, otherwise False.
        """

        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(email_regex, email) is not None

    def _is_valid_phone_number(phone_number: str) -> bool:
        """Check if the given phone number is valid based on regex pattern.

        Args:
            phone_number (str): phone number to be checked.

        Returns (bool): True if the phone number is valid, otherwise False.
        """

        pattern = r"\b(?:\+?\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}\b"
        return re.search(pattern, phone_number) is not None

    def _is_valid_credit_card(credit_card_number: str) -> bool:
        """Check if the given credit card number is valid based on regex pattern.

        Args:
            credit_card_number (str): credit card number to be checked.

        Returns (str): True if the credit card number is valid, otherwise False.
        """

        pattern = r"^\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}$"
        return re.search(pattern, credit_card_number) is not None

    def _generate_random_email() -> str:
        """Generates a random email address using predefined domains.

        Returns (str): generated random email address.
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

    def _generate_random_phone_number(original_field: str) -> str:
        """Generate a random phone number with country code if originally present.

        Args:
            original_field (str): original phone number field.

        Returns (str): generated random phone number.
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

    def _generate_random_credit_card() -> str:
        """Generate a random credit card number.

        Returns (str): generated random credit card number.
        """

        groups = []
        for _i in range(4):
            group = "".join(random.choices("0123456789", k=4))
            groups.append(group)
        separator = random.choice(["-", " "])
        return separator.join(groups)

    # static method to anonymize a dataframe head
    def anonymize_dataframe_head(df: pd.DataFrame) -> pd.DataFrame:
        """
        Anonymize a dataframe head by replacing the values of the columns
        that contain personal or sensitive information with random values.

        Args:
            df (pd.DataFrame): Dataframe to anonymize.

        Returns:
            pd.DataFrame: Anonymized dataframe.
        """

        if len(df) == 0:
            return df

        # create a copy of the dataframe head
        df_head = df.head().copy()

        # for each column, check if it contains personal or sensitive information
        # and if so, replace the values with random values
        for col in df_head.columns:
            if Anonymizer._is_valid_email(str(df_head[col].iloc[0])):
                df_head[col] = df_head[col].apply(
                    lambda x: Anonymizer._generate_random_email()
                )
            elif Anonymizer._is_valid_phone_number(str(df_head[col].iloc[0])):
                df_head[col] = df_head[col].apply(
                    lambda x: Anonymizer._generate_random_phone_number(str(x))
                )
            elif Anonymizer._is_valid_credit_card(str(df_head[col].iloc[0])):
                df_head[col] = df_head[col].apply(
                    lambda x: Anonymizer._generate_random_credit_card()
                )

        return df_head
