from pydantic import BaseModel, constr


class TaskCreate(BaseModel):
    title: constr(min_length=1, max_length=100)
    description: constr(min_length=1, max_length=1000)
