from fastapi import APIRouter

from app.application.chat.message_service import (
    MessageService,
)
from app.application.conversation.conversation_service import (
    ConversationService,
)
from app.schemas.message_request import (
    MessageRequest,
)
from app.schemas.message_response import (
    MessageResponse,
)

router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)

conversation_service = (
    ConversationService()
)

message_service = (
    MessageService()
)


@router.post("")
def create_conversation():

    conversation_id = (
        conversation_service.create()
    )

    return {
        "conversation_id": conversation_id,
    }


@router.get("/{conversation_id}")
def get_conversation(
    conversation_id: str,
):

    return conversation_service.get(
        conversation_id,
    )


@router.get("")
def list_conversations():

    return (
        conversation_service.list()
    )


@router.delete("/{conversation_id}")
def delete_conversation(
    conversation_id: str,
):

    conversation_service.delete(
        conversation_id,
    )

    return {
        "deleted": True,
    }


@router.post(
    "/{conversation_id}/messages",
    response_model=MessageResponse,
)
def send_message(
    conversation_id: str,
    request: MessageRequest,
) -> MessageResponse:

    return message_service.send(
        conversation_id=conversation_id,
        request=request,
    )


@router.get(
    "/{conversation_id}/messages",
    response_model=list[MessageResponse],
)
def get_messages(
    conversation_id: str,
):

    return message_service.history(
        conversation_id,
    )
