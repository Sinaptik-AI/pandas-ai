import os
from fastapi import HTTPException, UploadFile
from app.models import Dataset, ConnectorType
from app.repositories import DatasetRepository, WorkspaceRepository
from core.controller import BaseController
from core.exceptions.base import NotFoundException
from app.schemas.responses.datasets import WorkspaceDatasetsResponseModel, DatasetsDetailsResponseModel
from app.schemas.requests.datasets import DatasetUpdateRequestModel
import shutil
from app.schemas.responses.users import UserInfo
import csv
from core.database.transactional import Propagation, Transactional
from fastapi.responses import FileResponse

class DatasetController(BaseController[Dataset]):
    def __init__(
        self, 
        dataset_repository: DatasetRepository,
        space_repository: WorkspaceRepository
    ):
        super().__init__(model=Dataset, repository=dataset_repository)
        self.dataset_repository = dataset_repository
        self.space_repository = space_repository


    async def get_dataset_by_id(self, dataset_id: str):
        dataset = await self.dataset_repository.get_by_id(dataset_id)
        if not dataset:
            raise NotFoundException(
                "No dataset found with the given ID. Please check the ID and try again"
            )
        return dataset

    async def get_all_datasets(self) -> WorkspaceDatasetsResponseModel:
        datasets = await self.get_all()

        if not datasets:
            raise NotFoundException(
                "No dataset found. Please restart the server and try again"
            )

        return WorkspaceDatasetsResponseModel(datasets=datasets)
    
    async def get_datasets_details(self, dataset_id) -> DatasetsDetailsResponseModel:
        dataset = await self.get_dataset_by_id(dataset_id)
        return DatasetsDetailsResponseModel(dataset=dataset)
    
    @Transactional(propagation=Propagation.REQUIRED)
    async def delete_datasets(self, dataset_id, user):
        await self.get_dataset_by_id(dataset_id)
        await self.space_repository.delete_datasetspace(dataset_id, user.space.id)

        file_path = os.path.join(os.getcwd(), 'data', f"{dataset_id}.csv")
        if not os.path.exists(file_path):
            raise NotFoundException(
                "File not found!"
            )
        else:
            os.remove(file_path)

        return {"message": "Dataset deleted successfully"}
    

    async def update_dataset(self, dataset_id: str, dataset_update: DatasetUpdateRequestModel):
        dataset = await self.get_dataset_by_id(dataset_id)

        dataset.name = dataset_update.name
        dataset.description = dataset_update.description
        dataset = await self.dataset_repository.update_dataset(dataset=dataset)

        return {"message": "Dataset updated successfully"}
    

    @Transactional(propagation=Propagation.REQUIRED)
    async def create_dataset(self, file: UploadFile, name: str, description: str, user: UserInfo):
        headers = []
        rows = []
        try:
            file.file.seek(0)
            csvfile = (line.decode('utf-8') for line in file.file)
            csvreader = csv.reader(csvfile)
            headers = next(csvreader, None)
            if headers is None:
                raise HTTPException(status_code=400, detail="CSV file does not contain headers")
            for row in csvreader:
                rows.append(row)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to read file: {str(e)}")

        head = {
            "headers": headers,
            "rows": rows[:5]
        }

        dataset = await self.dataset_repository.create_dataset(
            user_id=user.id,
            organization_id=user.organizations[0].id,
            name=name,
            description=description,
            connector_type=ConnectorType.CSV,
            config={},
            head=head,
        )

        dataset_id = dataset.id
        file_path = os.path.join(os.getcwd(), 'data', f"{dataset_id}.csv")
        # Rewind the file and save it to disk
        file.file.seek(0)
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")
        
        await self.space_repository.add_dataset_to_space(workspace_id=user.space.id,dataset_id=dataset_id)

        return DatasetsDetailsResponseModel(dataset=dataset)
    

    async def download_dataset(self, dataset_id):
        await self.get_dataset_by_id(dataset_id)
        file_path = os.path.join(os.getcwd(), 'data', f"{dataset_id}.csv")

        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")

        return FileResponse(file_path, filename=f"{dataset_id}.csv", media_type='text/csv')