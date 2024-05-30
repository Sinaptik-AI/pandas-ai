from pydantic import UUID4, BaseModel


class SpaceBase(BaseModel):
    name: str
    id: UUID4
    slug: str
