from __future__ import annotations

from pathlib import Path

from app.knowledge_engine.connectors.base import BaseConnector
from app.knowledge_engine.connectors.registry import registry
from app.knowledge_engine.protocols.oai.client import OAIClient
from app.knowledge_engine.protocols.oai.normalizer import OAINormalizer
from app.knowledge_engine.protocols.oai.parser import OAIParser
from app.knowledge_engine.utils.downloader import Downloader
from app.schemas.attachment import DocumentAttachment
from app.schemas.document import DocumentMetadata


class BRABConnector(BaseConnector):
    """
    Connecteur OAI-PMH de la Bibliothèque de Recherches Agricoles du Bénin.
    """

    BASE_URL = "https://brab.bj/index.php/brab/oai"

    DOWNLOAD_DIR = (
        Path("data")
        / "documents"
        / "brab"
    )

    def __init__(self):
        super().__init__("brab")

        self.client = OAIClient(self.BASE_URL)
        self.parser = OAIParser()
        self.normalizer = OAINormalizer()
        self.downloader = Downloader()

    def discover(
        self,
    ) -> list[DocumentMetadata]:

        documents: list[DocumentMetadata] = []

        soup = self.client.list_records()

        while True:

            records = self.parser.parse_records(soup)

            for record in records:

                documents.append(
                    self.normalizer.normalize(
                        record,
                        source="BRAB",
                    )
                )

            token = self.parser.parse_resumption_token(
                soup
            )

            if token is None:
                break

            soup = self.client.list_records_from_token(
                token
            )

        return documents

    def download(
        self,
        document: DocumentMetadata,
    ) -> Path:
        """
        Télécharge le premier fichier associé au document.
        """

        if not document.attachments:
            raise ValueError(
                "Le document ne possède aucun fichier téléchargeable."
            )

        attachment: DocumentAttachment = document.attachments[0]

        self.DOWNLOAD_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        filename = (
            attachment.filename
            or "document.pdf"
        )

        destination = (
            self.DOWNLOAD_DIR
            / filename
        )

        return self.downloader.download_file(
            url=str(attachment.url),
            destination=destination,
        )


registry.register(
    "brab",
    BRABConnector,
)
