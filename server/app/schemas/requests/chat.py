from pydantic import BaseModel


class ChatRequest(BaseModel):
    space_id: str
    query: str
