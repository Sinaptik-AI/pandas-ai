from fastapi import APIRouter
from .workspaces import router as workspaces_router

router = APIRouter()
router.include_router(workspaces_router, prefix="/users")
