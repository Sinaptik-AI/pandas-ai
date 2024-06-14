from fastapi import status, HTTPException
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

        return ConversationMessageList(count=count, messages=list(reversed(conversation_messages)))
    
    async def archive_conversation(
        self, conversation_id: str, user_id: str
    ):
        user_conversation = (
            await self.conversation_repository.get_by_id(conversation_id)
        )
        if not user_conversation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            message=f"conversation with id: {conversation_id} was not found")
        if user_conversation.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            message="Unauthorized to update conversation for this user")
        user_conversation.valid = False
        await self.conversation_repository.session.commit()