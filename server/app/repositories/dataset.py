from app.models.user import Connector, ConnectorType, Dataset
from core.repository import BaseRepository


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
        )

        self.session.add(dataset)
        await self.session.flush()
        return dataset
