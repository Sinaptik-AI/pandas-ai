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
