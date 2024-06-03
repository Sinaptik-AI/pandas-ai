from typing import Any, Dict, List
from app.models import ConversationMessage, UserConversation
from core.repository import BaseRepository
from sqlalchemy.sql.expression import select


class ConversationRepository(BaseRepository[UserConversation]):
    """
    UserConversation repository provides all the database operations for the UserConversation model.
    """

    async def add_conversation_message(
        self,
        conversation_id: str,
        query: str,
        response: List[Dict],
        code_generated: str,
        **attributes: Any,
    ):
        conversation_message = ConversationMessage(
            conversation_id=conversation_id,
            query=query,
            response=response,
            code_generated=code_generated,
            **attributes,
        )

        self.session.add(conversation_message)

        return conversation_message

    async def get_conversation_messages(self, conversation_id: str):
        query = select(ConversationMessage).where(
            ConversationMessage.conversation_id == conversation_id
        )
        result = await self.session.execute(query)
        return result.scalars().all()
