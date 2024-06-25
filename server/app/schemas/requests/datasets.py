from pydantic import BaseModel
from typing import Optional
from fastapi import UploadFile, File

class DatasetUpdateRequestModel(BaseModel):
    name: str
    description: Optional[str] = None



class DatasetCreateRequestModel(BaseModel):
    name: str
    description: Optional[str] = None
    file: UploadFile = File(...),
