"""
This module contains helper functions related to plotting / charting.
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