from app.models.user import APIKeys
from core.repository import BaseRepository


class APIKeyRepository(BaseRepository[APIKeys]):
    """
    APIKeys repository provides all the database operations for the APIKeys model.
    """
