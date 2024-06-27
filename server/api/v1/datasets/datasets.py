from fastapi import APIRouter, Depends, Path, status, UploadFile, File, Form
from typing import Optional
from app.controllers.datasets import DatasetController
from app.schemas.responses.datasets import WorkspaceDatasetsResponseModel, DatasetsDetailsResponseModel
from core.factory import Factory
from uuid import UUID
from app.schemas.requests.datasets import DatasetUpdateRequestModel
from app.schemas.responses.users import UserInfo
from core.fastapi.dependencies.current_user import get_current_user
from fastapi.responses import FileResponse

dataset_router = APIRouter()

@dataset_router.get("/", response_model=WorkspaceDatasetsResponseModel)
async def get_all_datasets(datasets_controller: DatasetController = Depends(Factory().get_datasets_controller)):
    return await datasets_controller.get_all_datasets()


@dataset_router.get("/{dataset_id}", response_model=DatasetsDetailsResponseModel)
async def get_dataset(
        dataset_id: UUID = Path(..., description="ID of the dataset"),
        datasets_controller: DatasetController = Depends(Factory().get_datasets_controller)
    ):
    return await datasets_controller.get_datasets_details(dataset_id)


@dataset_router.post("/")
async def create_dataset(
        name: str = Form(...),
        description: Optional[str] = Form(None),
        file: UploadFile = File(...),
        user: UserInfo = Depends(get_current_user),
        datasets_controller: DatasetController = Depends(Factory().get_datasets_controller)
    ):
    return await datasets_controller.create_dataset(file,name, description, user)

    
@dataset_router.delete("/{dataset_id}")
async def delete_datasets(
        dataset_id: UUID = Path(..., description="ID of the dataset"),
        user: UserInfo = Depends(get_current_user),
        datasets_controller: DatasetController = Depends(Factory().get_datasets_controller)
    ):
    return await datasets_controller.delete_datasets(dataset_id, user)



@dataset_router.put("/{dataset_id}", status_code=status.HTTP_200_OK)
async def update_datasets(
        dataset_update: DatasetUpdateRequestModel,
        dataset_id: UUID = Path(..., description="ID of the dataset"),
        datasets_controller: DatasetController = Depends(Factory().get_datasets_controller)
    ):
    return await datasets_controller.update_dataset(dataset_id, dataset_update)


@dataset_router.get("/download/{dataset_id}", response_class=FileResponse, status_code=status.HTTP_200_OK)
async def download_dataset(
        dataset_id: UUID = Path(..., description="ID of the dataset"),
        datasets_controller: DatasetController = Depends(Factory().get_datasets_controller)
    ):
    return await datasets_controller.download_dataset(dataset_id)