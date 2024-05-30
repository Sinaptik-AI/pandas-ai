from typing import List

from sqlalchemy import delete, select
from sqlalchemy.orm import joinedload

from app.models.user import Connector, Dataset, DatasetSpace, Space, UserSpace
from app.repositories.dataset import DatasetRepository
from core.config import config
from core.repository import BaseRepository


class SpaceRepository(BaseRepository[Space]):
    """
    Space repository provides all the database operations for the Space model.
    """

    async def create_default_space_in_org(
        self, organization_id: str, user_id: str
    ) -> Space:
        space = await self.get_all(limit=1)
        if space:
            return space[0]

        space = Space(
            name=config.DEFAULT_SPACE,
            user_id=user_id,
            organization_id=organization_id,
            slug=config.DEFAULT_SPACE,
        )
        self.session.add(space)
        await self.session.flush()

        user_space = UserSpace(user_id=user_id, space_id=space.id)

        self.session.add(user_space)

        return space

    async def delete_space_datasets(self, space_id: str) -> None:
        # Select the DatasetSpace entries for the given space_id
        query = select(DatasetSpace).where(DatasetSpace.space_id == space_id)
        result = await self.session.execute(query)
        dataset_spaces = result.scalars().all()

        if not dataset_spaces:
            return

        dataset_ids = [ds.dataset_id for ds in dataset_spaces]

        # Select the datasets to be deleted with their connectors
        datasets_query = (
            select(Dataset)
            .options(joinedload(Dataset.connector))
            .where(Dataset.id.in_(dataset_ids))
        )
        datasets_result = await self.session.execute(datasets_query)
        datasets = datasets_result.scalars().all()

        connector_ids = [
            dataset.connector.id for dataset in datasets if dataset.connector
        ]

        # Delete the DatasetSpace entries
        delete_dataset_space_query = delete(DatasetSpace).where(
            DatasetSpace.space_id == space_id
        )
        await self.session.execute(delete_dataset_space_query)

        delete_dataset_query = delete(Dataset).where(Dataset.id.in_(dataset_ids))
        await self.session.execute(delete_dataset_query)

        # Delete the Connector entries
        if connector_ids:
            delete_connector_query = delete(Connector).where(
                Connector.id.in_(connector_ids)
            )
            await self.session.execute(delete_connector_query)

        await self.session.commit()

    async def create_csv_datasets(self, datasets: List[dict]) -> None:
        dataset_repository = DatasetRepository(Dataset, db_session=self.session)
        for dataset in datasets:
            dataset_repository.create({**dataset})

    async def add_dataset_to_space(self, space_id: str, dataset_id: str):
        dataset_space = DatasetSpace(space_id=space_id, dataset_id=dataset_id)
        self.session.add(dataset_space)
