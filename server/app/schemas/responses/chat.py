from typing import Any

from pydantic import BaseModel


class ChatResponse(BaseModel):
    type: str
    value: Any
    message: str
