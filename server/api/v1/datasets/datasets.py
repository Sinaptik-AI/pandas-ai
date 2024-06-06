from fastapi import APIRouter, Depends, Path
from app.controllers.datasets import DatasetController
from app.schemas.responses.datasets import WorkspaceDatasetsResponseModel
from core.factory import Factory

dataset_router = APIRouter()

@dataset_router.get("/", response_model=WorkspaceDatasetsResponseModel)
async def get_datasets(datasets_controller: DatasetController = Depends(Factory().get_datasets_controller)):
    return await datasets_controller.get_all_datasets()
