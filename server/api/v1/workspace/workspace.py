from fastapi import APIRouter, Depends, Path
from uuid import UUID

from app.controllers.workspace import WorkspaceController
from core.factory import Factory
from app.schemas.responses.users import UserInfo
from core.fastapi.dependencies.current_user import get_current_user
from app.schemas.responses.users import WorkspaceUsersResponse
from app.schemas.responses.datasets import WorkspaceDatasetsResponseModel
from app.schemas.requests.workspace import WorkspaceCreateRequestModel

workspace_router = APIRouter()


@workspace_router.get("/list")
async def get_user_workspaces(
    workspace_controller: WorkspaceController = Depends(Factory().get_space_controller),
    user: UserInfo = Depends(get_current_user),
):
    return await workspace_controller.get_user_workspaces(user)


@workspace_router.get("/{workspace_id}/users", response_model=WorkspaceUsersResponse)
async def get_workspace_users(
    workspace_id: UUID = Path(..., description="ID of the workspace"),
    workspace_controller: WorkspaceController = Depends(Factory().get_space_controller),
    user: UserInfo = Depends(get_current_user),
):
    return await workspace_controller.get_workspace_users(workspace_id)


@workspace_router.get(
    "/{workspace_id}/datasets", response_model=WorkspaceDatasetsResponseModel
)
async def get_workspace_datasets(
    workspace_id: UUID = Path(..., description="ID of the workspace"),
    workspace_controller: WorkspaceController = Depends(Factory().get_space_controller),
):
    return await workspace_controller.get_workspace_datasets(workspace_id)


@workspace_router.get("/{workspace_id}/details")
async def get_workspace_details(
    workspace_id: UUID = Path(..., description="ID of the workspace"),
    workspace_controller: WorkspaceController = Depends(Factory().get_space_controller),
):
    return await workspace_controller.get_workspace_datails(workspace_id)


@workspace_router.delete("/{workspace_id}")
async def delete_workspace(
    workspace_id: UUID = Path(..., description="ID of the workspace"),
    workspace_controller: WorkspaceController = Depends(Factory().get_space_controller),
):
    return await workspace_controller.delete_workspace(workspace_id)


@workspace_router.post("/add")
async def add_workspace(
    workspace: WorkspaceCreateRequestModel,
    workspace_controller: WorkspaceController = Depends(Factory().get_space_controller),
    user: UserInfo = Depends(get_current_user),
):
    return await workspace_controller.add_workspace(workspace, user)


@workspace_router.put("/{workspace_id}/edit")
async def edit_workspace(
    workspace: WorkspaceCreateRequestModel,
    workspace_id: UUID = Path(..., description="ID of the workspace"),
    workspace_controller: WorkspaceController = Depends(Factory().get_space_controller),
):
    return await workspace_controller.edit_workspace(workspace_id, workspace)
