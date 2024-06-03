from typing import List
from pydantic import UUID4, BaseModel
from datetime import datetime


class ConversationMessageBase(BaseModel):
    id: UUID4
    query: str
    created_at: datetime

    class Config:
        orm_mode = True


class UserConversationBase(BaseModel):
    id: UUID4
    workspace_id: UUID4
    user_id: UUID4
    created_at: datetime
    valid: bool
    messages: List[ConversationMessageBase]

    class Config:
        orm_mode = True


class ConversationList(BaseModel):
    count: int
    conversations: List[UserConversationBase]
