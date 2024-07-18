from pydantic import BaseModel
from typing import List


class WorkspaceCreateRequestModel(BaseModel):
    name: str
    datasets: List[str]