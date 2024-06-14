from pydantic import BaseModel, Field


class Health(BaseModel):
    version: str = Field(..., example="1.0.0")
    status: str = Field(..., example="OK")
