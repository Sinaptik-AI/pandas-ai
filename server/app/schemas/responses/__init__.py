from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    status_code: int = Field(default=200, example=0)
    data: Optional[T] = Field(default=None, example={})
    message: Optional[str] = None
    error: Optional[str] = None
