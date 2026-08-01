from pathlib import Path

from app.integrations.clients.whatsapp_client import (
    WhatsAppClient,
)
from app.integrations.models.media_file import (
    MediaFile,
)


class MediaDownloader:

    def __init__(self):

        self.client = WhatsAppClient()

    def download(
        self,
        media_id: str,
        destination: str | Path,
        media_type: str = "audio",
        mime_type: str = "audio/ogg",
    ) -> MediaFile:

        destination = Path(destination)

        return self.client.download_media(
            media_id=media_id,
            destination=destination,
            media_type=media_type,
            mime_type=mime_type,
        )
