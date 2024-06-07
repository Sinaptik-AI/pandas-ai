import pytest
from unittest.mock import MagicMock, patch
from app.controllers import (
    AuthController,
    UserController,
    ChatController,
    WorkspaceController,
    DatasetController,
    ConversationController,
)
from app.repositories import (
    UserRepository,
    WorkspaceRepository,
    DatasetRepository,
    ConversationRepository,
)
from core.factory.factory import Factory


class TestFactory:
    @pytest.fixture
    def factory(self):
        with patch("core.database.get_session") as mock_get_session:
            mock_get_session.return_value = MagicMock()
            yield Factory()

    def test_get_user_controller(self, factory):
        user_controller = factory.get_user_controller()
        assert isinstance(user_controller, UserController)
        assert isinstance(user_controller.user_repository, UserRepository)
        assert isinstance(user_controller.space_repository, WorkspaceRepository)

    def test_get_space_controller(self, factory):
        space_controller = factory.get_space_controller()
        assert isinstance(space_controller, WorkspaceController)
        assert isinstance(space_controller.space_repository, WorkspaceRepository)
        assert isinstance(space_controller.dataset_repository, DatasetRepository)

    def test_get_auth_controller(self, factory):
        auth_controller = factory.get_auth_controller()
        assert isinstance(auth_controller, AuthController)
        assert isinstance(auth_controller.user_repository, UserRepository)

    def test_get_chat_controller(self, factory):
        chat_controller = factory.get_chat_controller()
        assert isinstance(chat_controller, ChatController)
        assert isinstance(chat_controller.user_repository, UserRepository)
        assert isinstance(chat_controller.space_repository, WorkspaceRepository)
        assert isinstance(
            chat_controller.conversation_repository, ConversationRepository
        )

    def test_get_datasets_controller(self, factory):
        datasets_controller = factory.get_datasets_controller()
        assert isinstance(datasets_controller, DatasetController)
        assert isinstance(datasets_controller.dataset_repository, DatasetRepository)

    def test_get_conversation_controller(self, factory):
        conversation_controller = factory.get_conversation_controller()
        assert isinstance(conversation_controller, ConversationController)
        assert isinstance(conversation_controller.user_repository, UserRepository)
        assert isinstance(
            conversation_controller.conversation_repository, ConversationRepository
        )
