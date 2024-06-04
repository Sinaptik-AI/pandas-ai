from fastapi import APIRouter, Depends
from typing import List

from app.controllers.workspace import WorkspaceController
from app.schemas.responses.users import UserInfo
from core.factory import Factory

router = APIRouter()

@router.get("/", response_model=List[UserInfo])
async def get_workspace_users(
    workspace_controller: WorkspaceController = Depends(Factory().get_workspace_controller),
):
    return await workspace_controller.get_workspace_users()
