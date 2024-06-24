from fastapi import APIRouter

from .conversations import conversation_router

users_router = APIRouter()
users_router.include_router(conversation_router, tags=["Conversation"])

__all__ = ["conversation_router"]
