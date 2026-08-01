from app.integrations.models.send_result import (
    SendResult,
)


class WhatsAppSender:

    def send_text(
        self,
        to: str,
        text: str,
    ) -> SendResult:

        #
        # Implémentation V1 :
        # Stub prêt à être remplacé
        # par la WhatsApp Cloud API.
        #

        return SendResult(
            message_id="",
            status="pending",
            success=False,
        )

    def send_audio(
        self,
        to: str,
        audio_url: str,
    ) -> SendResult:

        #
        # Implémentation V1 :
        # Stub prêt à être remplacé
        # par la WhatsApp Cloud API.
        #

        return SendResult(
            message_id="",
            status="pending",
            success=False,
        )
