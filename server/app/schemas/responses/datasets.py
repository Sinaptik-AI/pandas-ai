from pydantic import BaseModel, UUID4
from typing import Optional, List
from datetime import datetime

class DatasetModel(BaseModel):
    id: UUID4
    name: str
    table_name: str
    description: Optional[str]
    created_at: datetime
    head: Optional[dict]
    user_id: UUID4
    organization_id: UUID4
    connector_id: UUID4
    field_descriptions: Optional[dict]
    filterable_columns: Optional[dict]

    class Config:
        orm_mode = True

class WorkspaceDatasetsResponseModel(BaseModel):
    datasets: List[DatasetModel]

class DatasetsDetailsResponseModel(BaseModel):
    dataset: DatasetModel