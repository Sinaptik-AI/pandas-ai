from functools import partial

from fastapi import Depends

from app.controllers import AuthController, UserController
from app.controllers.chat import ChatController
from app.controllers.space import SpaceController
from app.models import Dataset, Organization, OrganizationMembership, Space, User
from app.repositories import UserRepository
from app.repositories.api_key import APIKeyRepository
from app.repositories.dataset import DatasetRepository
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
    dataset_repository = partial(DatasetRepository, Dataset)

    def get_user_controller(self, db_session=Depends(get_session)):
        return UserController(
            user_repository=self.user_repository(db_session=db_session),
            space_repository=self.space_repository(db_session=db_session),
        )

    def get_space_controller(self, db_session=Depends(get_session)):
        return SpaceController(
            space_repository=self.space_repository(db_session=db_session),
            dataset_repository=self.dataset_repository(db_session=db_session),
        )

    def get_auth_controller(self, db_session=Depends(get_session)):
        return AuthController(
            user_repository=self.user_repository(db_session=db_session),
        )

    def get_chat_controller(self, db_session=Depends(get_session)):
        return ChatController(
            user_repository=self.user_repository(db_session=db_session),
            space_repository=self.space_repository(db_session=db_session),
        )
