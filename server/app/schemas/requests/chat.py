from typing import Optional
from pydantic import BaseModel


class ChatRequest(BaseModel):
    workspace_id: str
    query: str
    conversation_id: Optional[str] = None
