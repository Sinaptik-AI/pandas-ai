from app.models import OrganizationMembership
from core.repository import BaseRepository


class OrganizationMembershipRepository(BaseRepository[OrganizationMembership]):
    """
    Organization repository provides all the database operations for the Organization model.
    """
