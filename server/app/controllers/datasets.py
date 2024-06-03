from app.models import Dataset
from app.repositories import DatasetRepository
from core.controller import BaseController
from core.exceptions.base import NotFoundException


class DatasetController(BaseController[Dataset]):
    def __init__(
        self, dataset_repository: DatasetRepository
    ):
        super().__init__(model=Dataset, repository=dataset_repository)
        self.dataset_repository = dataset_repository

    async def get_all_datasets(self):
        datasets = await self.get_all()

        if not datasets:
            raise NotFoundException(
                "No dataset found. Please restart the server and try again"
            )

        return {"data": datasets}
