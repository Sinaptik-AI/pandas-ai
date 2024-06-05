from fastapi import status, HTTPException
from app.models import Dataset
from app.repositories import DatasetRepository, WorkspaceRepository
from core.controller import BaseController
from core.exceptions.base import NotFoundException
from app.schemas.responses.datasets import WorkspaceDatasetsResponseModel
from typing import List
class DatasetController(BaseController[Dataset]):
    def __init__(
        self, 
        dataset_repository: DatasetRepository,
        space_repository: WorkspaceRepository
    ):
        super().__init__(model=Dataset, repository=dataset_repository)
        self.dataset_repository = dataset_repository
        self.space_repository = space_repository

    async def get_all_datasets(self) -> WorkspaceDatasetsResponseModel:
        datasets = await self.get_all()

        if not datasets:
            raise NotFoundException(
                "No dataset found. Please restart the server and try again"
            )

        return WorkspaceDatasetsResponseModel(datasets=datasets)
