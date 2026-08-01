from datetime import datetime
from uuid import uuid4

from app.multimodal.models.input_message import (
    InputMessage,
)
from app.multimodal.models.normalized_message import (
    NormalizedMessage,
)


class ContentNormalizer:

    def normalize(
        self,
        message: InputMessage,
        detected_language: str,
    ) -> NormalizedMessage:

        return NormalizedMessage(
            message_id=str(uuid4()),
            conversation_id=(
                message.conversation_id
                or ""
            ),
            user_id=(
                message.user_id
                or ""
            ),
            channel=message.channel,
            modality=message.modality,
            detected_language=detected_language,
            normalized_text=message.content.strip(),
            original_content=message.content,
            timestamp=(
                message.timestamp
                or datetime.utcnow()
            ),
        )
