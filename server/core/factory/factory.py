from functools import partial

from fastapi import Depends

from app.controllers import AuthController, UserController
from app.models import User
from app.models.user import Organization, OrganizationMembership, Space
from app.repositories import UserRepository
from app.repositories.api_key import APIKeyRepository
from app.repositories.organization import OrganizationRepository
from app.repositories.space import SpaceRepository
from core.database import get_session


class Factory:
    """
    This is the factory container that will instantiate all the controllers and
    repositories which can be accessed by the rest of the application.
    """

    # Repositories
    user_repository = partial(UserRepository, User)
    organization_repository = partial(OrganizationRepository, Organization)
    api_key_repository = partial(APIKeyRepository, Organization)
    org_membership_repository = partial(OrganizationMembership, Organization)
    space_repository = partial(SpaceRepository, Space)

    def get_user_controller(self, db_session=Depends(get_session)):
        return UserController(
            user_repository=self.user_repository(db_session=db_session),
            space_repository=self.space_repository(db_session=db_session),
        )

    def get_auth_controller(self, db_session=Depends(get_session)):
        return AuthController(
            user_repository=self.user_repository(db_session=db_session),
        )
