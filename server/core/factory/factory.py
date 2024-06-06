from functools import partial

from fastapi import Depends

from app.controllers import AuthController, UserController
from app.controllers.chat import ChatController
from app.controllers.conversation import ConversationController
from app.controllers.workspace import WorkspaceController
from app.controllers.datasets import DatasetController
from app.models import (
    Dataset,
    Organization,
    OrganizationMembership,
    Workspace,
    User,
    UserConversation,
)
from app.repositories import UserRepository
from app.repositories.api_key import APIKeyRepository
from app.repositories.conversation import ConversationRepository
from app.repositories.dataset import DatasetRepository
from app.repositories.organization import OrganizationRepository
from app.repositories.workspace import WorkspaceRepository
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
    space_repository = partial(WorkspaceRepository, Workspace)
    dataset_repository = partial(DatasetRepository, Dataset)
    conversation_repository = partial(ConversationRepository, UserConversation)
    datasets_repository = partial(ConversationRepository, UserConversation)

    def get_user_controller(self, db_session=Depends(get_session)):
        return UserController(
            user_repository=self.user_repository(db_session=db_session),
            space_repository=self.space_repository(db_session=db_session),
        )

    def get_space_controller(self, db_session=Depends(get_session)):
        return WorkspaceController(
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
            conversation_repository=self.conversation_repository(db_session=db_session),
        )
    
    def get_datasets_controller(self, db_session=Depends(get_session)):
        return DatasetController(
            dataset_repository=self.dataset_repository(db_session=db_session),
            space_repository=self.space_repository(db_session=db_session)
        )

    def get_conversation_controller(self, db_session=Depends(get_session)):
        return ConversationController(
            user_repository=self.user_repository(db_session=db_session),
            conversation_repository=self.conversation_repository(db_session=db_session),
        )
