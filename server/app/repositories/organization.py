from app.models import Organization
from core.repository import BaseRepository


class OrganizationRepository(BaseRepository[Organization]):
    """
    Organization repository provides all the database operations for the Organization model.
    """
