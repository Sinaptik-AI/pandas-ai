import uuid

from sqlalchemy import Select
from sqlalchemy.orm import joinedload

from app.models import (
    APIKeys,
    Organization,
    OrganizationMembership,
    OrganizationRole,
    User,
)
from core.config import config
from core.repository import BaseRepository
from core.security.password import PasswordHandler


class UserRepository(BaseRepository[User]):
    """
    User repository provides all the database operations for the User model.
    """

    async def get_by_email(
        self, email: str, join_: set[str] | None = None
    ) -> User | None:
        """
        Get user by email.

        :param email: Email.
        :param join_: Join relations.
        :return: User.
        """
        query = self._query(join_)
        query = query.filter(User.email == email)

        if join_ is not None:
            return await self._all_unique(query)

        return await self._one_or_none(query)

    def get_user_me_details(self) -> User:
        return

    async def create_and_init_dummy_user(self) -> User:
        # Create user
        password = PasswordHandler.hash(config.PASSWORD)
        user = User(
            email=config.EMAIL,
            password=password,
            first_name="pandasai",
            verified=True,
        )
        self.session.add(user)

        # Create organization
        organization = Organization(name="PandasAI", url="", is_default=True)
        self.session.add(organization)

        # Flush to ensure IDs are populated
        await self.session.flush()

        # Create API key
        api_token = PasswordHandler.hash(str(uuid.uuid4()))
        api_key = APIKeys(organization_id=organization.id, api_key=api_token)
        self.session.add(api_key)

        # Create user-organization membership
        user_organization = OrganizationMembership(
            user_id=user.id,
            organization_id=organization.id,
            role=OrganizationRole.MEMBER,
            verified=True,
        )

        self.session.add(user_organization)

        user.organization_id = organization.id

        return user

    def _join_memberships(self, query: Select) -> Select:
        """
        Join tasks.

        :param query: Query.
        :return: Query.
        """
        return query.options(
            joinedload(User.memberships).joinedload(OrganizationMembership.organization)
        )
