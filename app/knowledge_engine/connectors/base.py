from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from app.knowledge_engine.utils.downloader import Downloader
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
        document: DocumentMetadata,
    ) -> Path:
        """
        Télécharge le premier fichier associé
        au document.
        """

        if not document.attachments:
            raise ValueError(
                "Le document ne possède aucun fichier téléchargeable."
            )

        attachment = document.attachments[0]

        destination = (
            self.DOWNLOAD_ROOT
            / self.name
            / (
                attachment.filename
                or "document"
            )
        )

        return self.downloader.download_file(
            url=str(attachment.url),
            destination=destination,
        )
