from typing import Any, List, Optional
from pydantic import UUID4, BaseModel
from datetime import datetime


class ConversationMessageBase(BaseModel):
    id: UUID4
    query: str
    created_at: datetime

    class Config:
        orm_mode = True


class ConversationMessageDTO(ConversationMessageBase):
    response: Optional[Any] = None
    code_generated: Optional[str] = None
    label: Optional[str] = None
    log_id: Optional[UUID4] = None
    settings: Optional[Any] = None


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


class ConversationMessageList(BaseModel):
    count: int
    messages: List[ConversationMessageDTO]
