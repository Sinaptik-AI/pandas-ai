from typing import Optional
from fastapi import APIRouter, Depends, Path, Query

from app.controllers.conversation import ConversationController
from app.schemas.responses import APIResponse

from app.schemas.responses.conversation import ConversationList, ConversationMessageList
from app.schemas.responses.users import UserInfo
from core.factory import Factory
from core.fastapi.dependencies.current_user import get_current_user
from uuid import UUID

conversation_router = APIRouter()


@conversation_router.get("/")
async def conversations(
    conversation_controller: ConversationController = Depends(
        Factory().get_conversation_controller
    ),
    user: UserInfo = Depends(get_current_user),
    skip: Optional[int] = Query(0, description="Number of items to skip"),
    limit: Optional[int] = Query(10, description="Number of items to retrieve"),
) -> APIResponse[ConversationList]:
    response = await conversation_controller.get_workspace_conversations(
        user.id, user.space.id, skip, limit
    )
    return APIResponse(
        data=response, message="User conversations returned successfully!"
    )


@conversation_router.get("/{conv_id}/messages")
async def conversation_messages(
    conv_id: UUID = Path(..., description="ID of the conversation"),
    conversation_controller: ConversationController = Depends(
        Factory().get_conversation_controller
    ),
    skip: Optional[int] = Query(0, description="Number of items to skip"),
    limit: Optional[int] = Query(10, description="Number of items to retrieve"),
) -> APIResponse[ConversationMessageList]:
    response = await conversation_controller.get_conversation_messages(
        conv_id, skip, limit
    )
    return APIResponse(
        data=response, message="User conversation messages returned successfully!"
    )

@conversation_router.delete("/{conv_id}")
async def delete_conversation(
    conv_id: UUID = Path(..., description="ID of the conversation"),
    conversation_controller: ConversationController = Depends(
        Factory().get_conversation_controller
    ),
    user: UserInfo = Depends(get_current_user),

):
    response = await conversation_controller.archive_conversation(
        conv_id, user.id
    )
    return APIResponse(
        data=response, message="Conversation archived successfully"
    )