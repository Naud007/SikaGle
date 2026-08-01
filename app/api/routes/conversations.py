from fastapi import APIRouter

from app.application.conversation.conversation_service import (
    ConversationService,
)

router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)

service = ConversationService()


@router.post("")
def create_conversation():

    conversation_id = service.create()

    return {
        "conversation_id": conversation_id,
    }


@router.get("/{conversation_id}")
def get_conversation(
    conversation_id: str,
):

    return service.get(
        conversation_id,
    )


@router.get("")
def list_conversations():

    return service.list()


@router.delete("/{conversation_id}")
def delete_conversation(
    conversation_id: str,
):

    service.delete(
        conversation_id,
    )

    return {
        "deleted": True,
    }
