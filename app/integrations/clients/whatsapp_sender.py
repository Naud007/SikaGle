"""
SikaGlé

Client d'envoi des messages WhatsApp Cloud API.
"""

from __future__ import annotations

import requests

from app.core.config import settings
from app.integrations.models.send_result import (
    SendResult,
)


class WhatsAppSender:

    def __init__(self):

        self.token = settings.WHATSAPP_TOKEN

        self.phone_number_id = (
            settings.WHATSAPP_PHONE_NUMBER_ID
        )

        self.api_version = getattr(
            settings,
            "WHATSAPP_API_VERSION",
            "v18.0",
        )

    def send_text(
        self,
        to: str,
        text: str,
    ) -> SendResult:

        if (
            not self.token
            or not self.phone_number_id
        ):

            return SendResult(
                message_id="",
                status="missing_configuration",
                success=False,
            )

        url = (
            f"https://graph.facebook.com/"
            f"{self.api_version}/"
            f"{self.phone_number_id}/messages"
        )

        headers = {
            "Authorization": (
                f"Bearer {self.token}"
            ),
            "Content-Type": "application/json",
        }

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {
                "body": text,
            },
        }

        try:

            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=30,
            )

            if response.status_code != 200:

                return SendResult(
                    message_id="",
                    status=(
                        f"api_error_"
                        f"{response.status_code}"
                    ),
                    success=False,
                )

            data = response.json()

            messages = data.get(
                "messages",
                [],
            )

            message_id = ""

            if messages:

                message_id = messages[0].get(
                    "id",
                    "",
                )

            return SendResult(
                message_id=message_id,
                status="sent",
                success=True,
            )

        except Exception as exc:

            return SendResult(
                message_id="",
                status=f"error: {exc}",
                success=False,
            )

    def send_audio(
        self,
        to: str,
        audio_url: str,
    ) -> SendResult:

        if (
            not self.token
            or not self.phone_number_id
        ):

            return SendResult(
                message_id="",
                status="missing_configuration",
                success=False,
            )

        url = (
            f"https://graph.facebook.com/"
            f"{self.api_version}/"
            f"{self.phone_number_id}/messages"
        )

        headers = {
            "Authorization": (
                f"Bearer {self.token}"
            ),
            "Content-Type": "application/json",
        }

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "audio",
            "audio": {
                "link": audio_url,
            },
        }

        try:

            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=30,
            )

            if response.status_code != 200:

                return SendResult(
                    message_id="",
                    status=(
                        f"api_error_"
                        f"{response.status_code}"
                    ),
                    success=False,
                )

            data = response.json()

            messages = data.get(
                "messages",
                [],
            )

            message_id = ""

            if messages:

                message_id = messages[0].get(
                    "id",
                    "",
                )

            return SendResult(
                message_id=message_id,
                status="sent",
                success=True,
            )

        except Exception as exc:

            return SendResult(
                message_id="",
                status=f"error: {exc}",
                success=False,
            )