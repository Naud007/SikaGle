from pathlib import Path

from app.integrations.models.media_file import (
    MediaFile,
)


class WhatsAppClient:

    def download_media(
        self,
        media_id: str,
        destination: Path,
        media_type: str = "audio",
        mime_type: str = "audio/ogg",
    ) -> MediaFile:

        #
        # Implémentation V1 :
        # Stub prêt à être remplacé
        # par les appels à la WhatsApp Cloud API.
        #

        return MediaFile(
            media_id=media_id,
            media_type=media_type,
            file_path=destination,
            mime_type=mime_type,
            downloaded=False,
        )
