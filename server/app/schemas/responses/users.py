from typing import List, Optional

from pydantic import UUID4, BaseModel, Field

from app.schemas.responses.organization import OrganizationBase
from app.schemas.responses.space import SpaceBase


class UserResponse(BaseModel):
    email: str = Field(..., example="john.doe@example.com")
    username: str = Field(..., example="john.doe")
    uuid: UUID4 = Field(..., example="a3b8f042-1e16-4f0a-a8f0-421e16df0a2f")

    class Config:
        orm_mode = True


class MembershipBase(BaseModel):
    organization: OrganizationBase

    class Config:
        orm_mode = True


class UserInfo(BaseModel):
    email: str = Field(..., example="john.doe@example.com")
    first_name: str = Field(..., example="john.doe")
    id: UUID4 = Field(..., example="a3b8f042-1e16-4f0a-a8f0-421e16df0a2f")
    organizations: List[OrganizationBase] = Field(...)
    space: SpaceBase = Field(...)

    class Config:
        orm_mode = True


class WorkspaceUserResponse(BaseModel):
    id: UUID4
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]

    class Config:
        orm_mode = True

class WorkspaceUsersResponse(BaseModel):
    users: List[WorkspaceUserResponse]