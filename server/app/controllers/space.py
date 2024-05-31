from typing import List

from app.models import User
from app.models.user import ConnectorType, Space
from app.repositories.dataset import DatasetRepository
from app.repositories.space import SpaceRepository
from core.controller import BaseController
from core.database.transactional import Propagation, Transactional


class SpaceController(BaseController[Space]):
    def __init__(
        self, space_repository: SpaceRepository, dataset_repository: DatasetRepository
    ):
        super().__init__(model=User, repository=space_repository)
        self.space_repository = space_repository
        self.dataset_repository = dataset_repository

    @Transactional(propagation=Propagation.REQUIRED_NEW)
    async def reset_space_datasets(self, space_id: str) -> bool:
        await self.space_repository.delete_space_datasets(space_id)
        return True

    @Transactional(propagation=Propagation.REQUIRED_NEW)
    async def add_csv_datasets(self, datasets: List[dict], user: User, space_id: str):
        for dataset in datasets:
            dataset = await self.dataset_repository.create_dataset(
                user_id=user.id,
                organization_id=user.memberships[0].organization_id,
                name=dataset["file_name"],
                connector_type=ConnectorType.CSV,
                config={
                    "file_path": dataset["file_path"],
                    "file_name": dataset["file_name"],
                },
                head=dataset["head"],
            )
            await self.space_repository.add_dataset_to_space(
                dataset_id=dataset.id, space_id=space_id
            )
