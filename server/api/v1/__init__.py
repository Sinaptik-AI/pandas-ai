from fastapi import APIRouter

from .chat import chat_router
from .monitoring import monitoring_router
from .users import users_router
from .datasets import datasets_router
from .conversations import conversation_router
from .workspace import workspaces_router

v1_router = APIRouter()
v1_router.include_router(monitoring_router, prefix="/monitoring")
v1_router.include_router(users_router, prefix="/users")
v1_router.include_router(chat_router, prefix="/chat", tags=["Chat"])
v1_router.include_router(datasets_router, prefix="/datasets", tags=["Dataset"])
v1_router.include_router(
    conversation_router, prefix="/conversations", tags=["Conversations"]
)
v1_router.include_router(
    workspaces_router, prefix="/workspace", tags=["Workspace"]
)
