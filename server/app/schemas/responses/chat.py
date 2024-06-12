from typing import Any, List

from pydantic import BaseModel


class ChatResponseBase(BaseModel):
    type: str
    value: Any
    message: str


class ChatResponse(BaseModel):
    response: List[ChatResponseBase]
    conversation_id: str
    message_id: str
    query: str
