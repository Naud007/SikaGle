import os
from pathlib import Path

import requests

from app.integrations.models.media_file import (
    MediaFile,
)


class WhatsAppClient:

    def __init__(self):

        self.token = os.getenv(
            "WHATSAPP_TOKEN",
            "",
        )

        self.phone_id = os.getenv(
            "WHATSAPP_PHONE_ID",
            os.getenv(
                "WHATSAPP_PHONE_NUMBER_ID",
                "",
            ),
        )

        self.graph_url = (
            "https://graph.facebook.com/v18.0"
        )

    def download_media(
        self,
        media_id: str,
        destination: Path,
        media_type: str = "audio",
        mime_type: str = "audio/ogg",
    ) -> MediaFile:

        destination = Path(destination)

        if not self.token:
            raise ValueError(
                "WHATSAPP_TOKEN est manquante."
            )

        # 1. Récupérer l'URL temporaire du média
        media_response = requests.get(
            f"{self.graph_url}/{media_id}",
            headers={
                "Authorization": f"Bearer {self.token}",
            },
            timeout=30,
        )

        media_response.raise_for_status()

        media_data = media_response.json()

        media_url = media_data.get("url")

        if not media_url:
            raise ValueError(
                "WhatsApp n'a retourné aucune URL média."
            )

        # 2. Télécharger réellement le fichier
        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        file_response = requests.get(
            media_url,
            headers={
                "Authorization": f"Bearer {self.token}",
            },
            timeout=60,
        )

        file_response.raise_for_status()

        destination.write_bytes(
            file_response.content
        )

        return MediaFile(
            media_id=media_id,
            media_type=media_type,
            file_path=destination,
            mime_type=(
                media_data.get(
                    "mime_type",
                    mime_type,
                )
            ),
            downloaded=True,
        )