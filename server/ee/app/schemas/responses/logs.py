from pydantic import UUID4, BaseModel, Field
from typing import Optional, List
from datetime import datetime


class LogResponse(BaseModel):
    id: UUID4 = Field(..., example="a3b8f042-1e16-4f0a-a8f0-421e16df0a2f")
    created_at: datetime
    query: Optional[str]
    execution_time: Optional[float]
    success: Optional[bool]
    json_log: Optional[dict]

    class Config:
        orm_mode = True


class LogsResponse(BaseModel):
    id: UUID4 = Field(..., example="a3b8f042-1e16-4f0a-a8f0-421e16df0a2f")
    created_at: datetime
    query: Optional[str]
    execution_time: Optional[float]
    success: Optional[bool]

    class Config:
        orm_mode = True


class LogsResponseModel(BaseModel):
    message: str
    logs_count: int
    logs: List[LogsResponse]


class LogResponseModel(BaseModel):
    message: str
    log: LogResponse
