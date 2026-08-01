from pathlib import Path

from app.integrations.media.media_downloader import (
    MediaDownloader,
)
from app.integrations.models.media_file import (
    MediaFile,
)


class MediaService:

    def __init__(self):

        self.downloader = (
            MediaDownloader()
        )

    def download(
        self,
        media_id: str,
        destination: str | Path,
        media_type: str = "audio",
        mime_type: str = "audio/ogg",
    ) -> MediaFile:

        return self.downloader.download(
            media_id=media_id,
            destination=destination,
            media_type=media_type,
            mime_type=mime_type,
        )
