from app.integrations.clients.whatsapp_sender import (
    WhatsAppSender,
)
from app.integrations.models.send_result import (
    SendResult,
)


class ResponseSender:

    def __init__(self):

        self.sender = WhatsAppSender()

    def send_text(
        self,
        to: str,
        text: str,
    ) -> SendResult:

        return self.sender.send_text(
            to=to,
            text=text,
        )

    def send_audio(
        self,
        to: str,
        audio_url: str,
    ) -> SendResult:

        return self.sender.send_audio(
            to=to,
            audio_url=audio_url,
        )
