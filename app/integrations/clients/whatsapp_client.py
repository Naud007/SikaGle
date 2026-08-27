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

        # =========================================================
        # 1. RÉCUPÉRER L'URL TEMPORAIRE DU MÉDIA
        # =========================================================

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

        # =========================================================
        # 2. RÉCUPÉRER LE MIME TYPE
        # =========================================================

        whatsapp_mime_type = media_data.get(
            "mime_type",
            mime_type,
        )

        # WhatsApp peut retourner :
        # audio/ogg; codecs=opus
        #
        # Pour Gemini, on conserve uniquement :
        # audio/ogg

        if whatsapp_mime_type:
            whatsapp_mime_type = (
                whatsapp_mime_type
                .split(";")[0]
                .strip()
                .lower()
            )

        if not whatsapp_mime_type:
            whatsapp_mime_type = "audio/ogg"

        # =========================================================
        # 3. TÉLÉCHARGER RÉELLEMENT LE FICHIER
        # =========================================================

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

        print(
            "🎧 Média WhatsApp téléchargé :",
            destination,
        )

        print(
            "🎧 MIME type :",
            whatsapp_mime_type,
        )

        # =========================================================
        # 4. RETOURNER LE MÉDIA
        # =========================================================

        return MediaFile(
            media_id=media_id,
            media_type=media_type,
            file_path=destination,
            mime_type=whatsapp_mime_type,
            downloaded=True,
        )

    # =========================================================
    # UPLOAD D'UN MÉDIA (ex : réponse audio générée par SikaGlé)
    #
    # NOTE :
    #
    # Étape nécessaire avant de pouvoir envoyer un message
    # audio : WhatsApp exige d'abord que le fichier soit
    # uploadé sur ses serveurs, ce qui retourne un media_id
    # à utiliser ensuite dans l'envoi du message.
    # =========================================================

    def upload_media(
        self,
        file_path: Path,
        mime_type: str = "audio/mpeg",
    ) -> str:

        file_path = Path(file_path)

        if not self.token:
            raise ValueError(
                "WHATSAPP_TOKEN est manquante."
            )

        if not self.phone_id:
            raise ValueError(
                "WHATSAPP_PHONE_ID est manquante."
            )

        if not file_path.exists():
            raise FileNotFoundError(
                f"Fichier introuvable : {file_path}"
            )

        url = (
            f"{self.graph_url}/{self.phone_id}/media"
        )

        with open(
            file_path,
            "rb",
        ) as f:

            files = {
                "file": (
                    file_path.name,
                    f,
                    mime_type,
                ),
            }

            data = {
                "messaging_product": "whatsapp",
                "type": mime_type,
            }

            response = requests.post(
                url,
                headers={
                    "Authorization": (
                        f"Bearer {self.token}"
                    ),
                },
                files=files,
                data=data,
                timeout=60,
            )

        response.raise_for_status()

        result = response.json()

        media_id = result.get("id")

        if not media_id:
            raise ValueError(
                "WhatsApp n'a retourné aucun media_id "
                "après l'upload."
            )

        print(
            "🎧 Média uploadé vers WhatsApp, media_id :",
            media_id,
        )

        return media_id