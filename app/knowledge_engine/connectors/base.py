from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from app.knowledge_engine.utils.downloader import Downloader
from app.schemas.attachment import DocumentAttachment
from app.schemas.document import DocumentMetadata


class BaseConnector(ABC):
    """
    Classe de base de tous les connecteurs.
    """

    DOWNLOAD_ROOT = Path("data") / "documents"

    def __init__(
        self,
        name: str,
    ):
        self.name = name
        self.downloader = Downloader()

    @abstractmethod
    def discover(
        self,
    ) -> list[DocumentMetadata]:
        """
        Découvre les documents disponibles.
        """
        raise NotImplementedError()

    def download(
        self,
        attachment: DocumentAttachment,
    ) -> Path:
        """
        Télécharge une pièce jointe.
        """

        filename = (
            attachment.filename
            or "document"
        )

        destination = (
            self.DOWNLOAD_ROOT
            / self.name
            / filename
        )

        return self.downloader.download_file(
            url=str(attachment.url),
            destination=destination,
        )

    def download_document(
        self,
        document: DocumentMetadata,
    ) -> list[Path]:
        """
        Télécharge toutes les pièces jointes d'un document.
        """

        if not document.attachments:
            return []

        paths = []

        for attachment in document.attachments:
            paths.append(
                self.download(
                    attachment,
                )
            )

        return paths
