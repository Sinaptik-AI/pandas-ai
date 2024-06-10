from typing import Any, Dict, List

from sqlalchemy import and_, asc, desc, func
from app.models import ConversationMessage, UserConversation
from core.repository import BaseRepository
from sqlalchemy.sql.expression import select
from sqlalchemy.orm import selectinload
from core.database.transactional import Propagation, Transactional


class ConversationRepository(BaseRepository[UserConversation]):
    """
    UserConversation repository provides all the database operations for the UserConversation model.
    """
    @Transactional(propagation=Propagation.REQUIRED)
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

    async def get_conversation_messages(
        self, conversation_id: str, skip: int = 0, limit: int = 100, order: str = "asc"
    ):
        order_by_clause = (
            desc(ConversationMessage.created_at)
            if order == "desc"
            else asc(ConversationMessage.created_at)
        )

        query = (
            select(ConversationMessage)
            .where(ConversationMessage.conversation_id == conversation_id)
            .order_by(order_by_clause)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_conversations(
        self, user_id: str, workspace_id: str, skip: int = 0, limit: int = 100
    ) -> List[UserConversation]:
        query = (
            select(UserConversation)
            .where(
                and_(
                    UserConversation.user_id == user_id,
                    UserConversation.valid == True,
                    UserConversation.workspace_id == workspace_id,
                )
            )
            .order_by(desc(UserConversation.created_at))
            .options(
                selectinload(UserConversation.messages).load_only(
                    ConversationMessage.id,
                    ConversationMessage.query,
                    ConversationMessage.created_at,
                ),
            )
            .offset(skip)
            .limit(limit)
        )

        result = await self.session.execute(query)
        conversations = result.scalars().all()

        for conversation in conversations:
            if conversation.messages:
                conversation.messages.sort(key=lambda msg: msg.created_at)
                conversation.messages = conversation.messages[:1]

        return conversations

    async def get_count(self, user_id: str, workspace_id: str) -> int:
        query = select(func.count(UserConversation.id)).where(
            and_(
                UserConversation.user_id == user_id,
                UserConversation.workspace_id == workspace_id,
                UserConversation.valid == True,
            )
        )

        result = await self.session.execute(query)
        return result.scalar_one()

    async def get_messages_count(self, conversation_id: str) -> int:
        query = select(func.count(ConversationMessage.id)).where(
            ConversationMessage.conversation_id == conversation_id
        )

        result = await self.session.execute(query)
        return result.scalar_one()
