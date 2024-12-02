import re
import unicodedata


def create_slug(text: str) -> str:
    """
    Generate a slug from a given text.

    Args:
        text (str): The input text to convert into a slug.

    Returns:
        str: A URL-friendly slug.
    """
    # Normalize text to remove accents and special characters
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")

    # Convert to lowercase
    text = text.lower()

    # Replace spaces and unwanted characters with a hyphen
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text.strip())

    # Remove leading or trailing hyphens
    return text.strip("-")
