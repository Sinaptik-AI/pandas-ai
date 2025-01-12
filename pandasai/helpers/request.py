"""Request helper module."""

from typing import Optional
import requests


def get_pandaai_session(api_key: Optional[str] = None) -> requests.Session:
    """Get a requests session with the PandaAI API key.

    Args:
        api_key (Optional[str], optional): API key for PandaAI. Defaults to None.

    Returns:
        requests.Session: Session with API key.
    """
    session = requests.Session()
    if api_key:
        session.headers.update({"Authorization": f"Bearer {api_key}"})
    return session
