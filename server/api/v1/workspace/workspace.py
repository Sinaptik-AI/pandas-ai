from fastapi import APIRouter, Depends

from app.controllers.workspace import WorkspaceController
from core.factory import Factory
from app.schemas.responses.users import UserInfo
from core.fastapi.dependencies.current_user import get_current_user

workspace_router = APIRouter()


@workspace_router.get("/users")
async def get_workspace_users(
    workspace_controller: WorkspaceController = Depends(
        Factory().get_space_controller
    ),
    user: UserInfo = Depends(get_current_user)):
    return await workspace_controller.get_workspace_users(user.space.id)
