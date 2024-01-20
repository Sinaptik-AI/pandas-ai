import sys

from dotenv import load_dotenv as _load_dotenv

from .path import find_closest


def load_dotenv():
    """
    Load the .env file from the root folder of the project
    """
    try:
        dotenv_path = find_closest(".env")
        _load_dotenv(dotenv_path=dotenv_path)
    except ValueError:
        pass


def is_running_in_console() -> bool:
    """
    Check if the code is running in console or not.

    Returns:
        bool: True if running in console else False
    """

    return sys.stdout.isatty()
