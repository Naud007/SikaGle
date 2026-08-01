from datetime import datetime

from app.integrations.models.whatsapp_message import (
    WhatsAppMessage,
)
from app.multimodal.models.input_message import (
    InputMessage,
)


class MessageNormalizer:

    def normalize(
        self,
        message: WhatsAppMessage,
    ) -> InputMessage:

        return InputMessage(
            content=message.content,
            modality=message.message_type,
            channel="whatsapp",
            timestamp=datetime.fromtimestamp(
                int(message.timestamp)
            ),
            user_id=message.from_number,
            conversation_id=message.message_id,
        )
