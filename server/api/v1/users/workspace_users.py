from fastapi import APIRouter, Depends, HTTPException
from typing import List

from app.controllers.workspace import WorkspaceController
from app.schemas.responses.users import UserInfo
from core.factory import Factory
from core.fastapi.dependencies.current_user import get_current_user

router = APIRouter()

@router.get("/", response_model=List[UserInfo])
async def get_workspace_users(
    workspace_id: str,
    workspace_controller: WorkspaceController = Depends(Factory().get_workspace_controller),
    current_user: UserInfo = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized access")
    try:
        users = await workspace_controller.get_users_by_workspace_id(workspace_id)
        return users
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
