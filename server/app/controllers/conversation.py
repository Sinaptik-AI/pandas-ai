from app.models import User, UserConversation
from app.repositories import UserRepository
from app.repositories.conversation import ConversationRepository

from app.schemas.responses.conversation import ConversationList, ConversationMessageList
from core.controller import BaseController


class ConversationController(BaseController[UserConversation]):
    def __init__(
        self,
        user_repository: UserRepository,
        conversation_repository: ConversationRepository,
    ):
        super().__init__(model=User, repository=user_repository)
        self.user_repository = user_repository
        self.conversation_repository = conversation_repository

    async def get_workspace_conversations(
        self, user_id: str, workspace_id: str, skip: int = 0, limit: int = 100
    ) -> ConversationList:
        conversations = await self.conversation_repository.get_conversations(
            user_id, workspace_id, skip, limit
        )

        count = await self.conversation_repository.get_count(user_id, workspace_id)
        return ConversationList(count=count, conversations=conversations)

    async def get_conversation_messages(
        self, conversation_id: str, skip: int = 0, limit: int = 100
    ):
        conversation_messages = (
            await self.conversation_repository.get_conversation_messages(
                conversation_id, skip, limit, "desc"
            )
        )

        count = await self.conversation_repository.get_messages_count(conversation_id)

        return ConversationMessageList(count=count, messages=conversation_messages)
