from app.models import Connector, ConnectorType, Dataset, DatasetSpace
from core.repository import BaseRepository
from uuid import UUID
from sqlalchemy import select


class DatasetRepository(BaseRepository[Dataset]):
    """
    Dataset repository provides all the database operations for the Dataset model.
    """

    async def create_dataset(
        self,
        user_id: str,
        organization_id: str,
        name: str,
        connector_type: ConnectorType,
        config,
        head: dict,
        description: str = "",
    ):
        connector = Connector(type=connector_type.value, config=config, user_id=user_id)
        self.session.add(connector)
        await self.session.flush()

        dataset = Dataset(
            name=name,
            table_name=name,
            head=head,
            user_id=user_id,
            organization_id=organization_id,
            connector_id=connector.id,
            description=description
        )

        self.session.add(dataset)
        await self.session.flush()
        return dataset

    async def get_all_by_workspace_id(self, workspace_id: UUID):
        result = await self.session.execute(
            select(Dataset).join(DatasetSpace).where(DatasetSpace.workspace_id == workspace_id)
        )
        datasets = result.scalars().all()
        return datasets
    

    async def update_dataset(self, dataset):
        self.session.add(dataset)
        await self.session.commit()
        await self.session.refresh(dataset)

        return dataset

