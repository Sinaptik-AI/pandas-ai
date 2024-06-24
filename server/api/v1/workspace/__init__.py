from fastapi import APIRouter

from .workspace import workspace_router

workspaces_router = APIRouter()
workspaces_router.include_router(workspace_router, tags=["Workspace"])

__all__ = ["workspace_router"]
