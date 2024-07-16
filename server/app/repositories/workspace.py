from fastapi import HTTPException
from typing import List
from sqlalchemy import delete, select, update
from sqlalchemy.orm import joinedload

from app.models import Connector, Dataset, DatasetSpace, Workspace, UserSpace, User
from app.repositories.dataset import DatasetRepository
from core.config import config
from core.repository import BaseRepository
from app.schemas.responses.users import WorkspaceUserResponse
from core.database.transactional import Propagation, Transactional

class WorkspaceRepository(BaseRepository[Workspace]):
    """
    Space repository provides all the database operations for the Space model.
    """

    async def create_default_space_in_org(
        self, organization_id: str, user_id: str
    ) -> Workspace:
        space = await self.get_all(limit=1)
        if space:
            return space[0]

        space = Workspace(
            name=config.DEFAULT_SPACE,
            user_id=user_id,
            organization_id=organization_id,
            slug=config.DEFAULT_SPACE,
        )
        self.session.add(space)
        await self.session.flush()

        user_space = UserSpace(user_id=user_id, workspace_id=space.id)

        self.session.add(user_space)

        return space

    async def delete_space_datasets(self, workspace_id: str) -> None:
        # Select the DatasetSpace entries for the given workspace_id
        query = select(DatasetSpace).where(DatasetSpace.workspace_id == workspace_id)
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
            DatasetSpace.workspace_id == workspace_id
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

    async def add_dataset_to_space(self, workspace_id: str, dataset_id: str):
        dataset_space = DatasetSpace(workspace_id=workspace_id, dataset_id=dataset_id)
        self.session.add(dataset_space)

    async def get_space_datasets(self, workspace_id: str) -> List[Dataset]:
        result = await self.session.execute(
            select(Dataset)
            .join(DatasetSpace)
            .options(joinedload(Dataset.dataset_spaces))
            .filter(DatasetSpace.workspace_id == workspace_id)
        )
        return result.unique().scalars().all()

    async def get_users_by_workspace_id(self, workspace_id: str) -> List[WorkspaceUserResponse]:
        result = await self.session.execute(
            select(
                User.id,
                User.first_name,
                User.last_name,
                User.email
            ).join(UserSpace).filter(UserSpace.workspace_id == workspace_id)
        )
        return result.all()
    

    async def delete_datasetspace(self, dataset_id: str, workspace_id: str):
        await self.session.execute(
            delete(DatasetSpace).where(
                DatasetSpace.dataset_id == dataset_id,
                DatasetSpace.workspace_id == workspace_id
            )
        )

        # Delete the Dataset entry
        await self.session.execute(
            delete(Dataset).where(Dataset.id == dataset_id)
        )

    async def get_user_workspaces(self, user):
        space_result = await self.session.execute(
            select(Workspace).filter(Workspace.user_id == user.id)
        )
        user_spaces = space_result.scalars().all()


        return user_spaces
    

    async def get_workspace_datails(self, workspace_id: str):
        result = await self.session.execute(
            select(Workspace)
            .options(
                joinedload(Workspace.dataset_spaces)
                .joinedload(DatasetSpace.dataset)
                .joinedload(Dataset.connector)
            )
            .where(Workspace.id == workspace_id)
        )
        workspace = result.scalars().first()
        if not workspace:
            raise HTTPException(status_code=404, detail="Workspace not found")
        return workspace
    

    
    async def delete_workspace(self, workspace_id: str):
       async with self.session.begin():
            result = await self.session.execute(
                select(Workspace)
                .options(
                    joinedload(Workspace.dataset_spaces),
                    joinedload(Workspace.user_spaces)
                )
                .where(Workspace.id == workspace_id)
            )
            workspace = result.scalars().first()

            if not workspace:
                raise HTTPException(status_code=404, detail="Workspace not found")

            for dataset_space in workspace.dataset_spaces:
                await self.session.delete(dataset_space)

            for user_space in workspace.user_spaces:
                await self.session.delete(user_space)

            await self.session.delete(workspace)
            await self.session.commit()



    @Transactional(propagation=Propagation.REQUIRED_NEW)
    async def create_workspace(self, workspace_data, user):
        new_workspace = Workspace(
            name=workspace_data.name,
            user_id=user.id,
            organization_id=user.organizations[0].id,
        )
        self.session.add(new_workspace)
        await self.session.flush()

        dataset_spaces = [
            DatasetSpace(workspace_id=new_workspace.id, dataset_id=dataset_id)
            for dataset_id in workspace_data.datasets
        ]
        self.session.add_all(dataset_spaces)

        user_space = UserSpace(workspace_id=new_workspace.id, user_id=user.id)
        self.session.add(user_space)

        return new_workspace
    

    @Transactional(propagation=Propagation.REQUIRED_NEW)
    async def edit_workspace(self, workspace_id, workspace_data):
        async with self.session.begin():
            result = await self.session.execute(
                select(Workspace)
                .options(
                    joinedload(Workspace.dataset_spaces),
                )
                .where(Workspace.id == workspace_id)
            )
            workspace = result.scalars().first()

            if not workspace:
                raise HTTPException(status_code=404, detail="Workspace not found")
            
            await self.session.execute(
                delete(DatasetSpace).where(DatasetSpace.workspace_id == workspace_id)
            )

            update_data = {
                Workspace.name: workspace_data.name
            }

            await self.session.execute(
                update(Workspace)
                .where(Workspace.id == workspace_id)
                .values(update_data)
            )
            dataset_spaces = [
                DatasetSpace(workspace_id=workspace_id, dataset_id=dataset_id)
                for dataset_id in workspace_data.datasets
            ]
            self.session.add_all(dataset_spaces)
            await self.session.commit()
            return workspace
