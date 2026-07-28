from __future__ import annotations

from pathlib import Path

from app.knowledge_engine.connectors.registry import registry
from app.schemas.attachment import DocumentAttachment
from app.schemas.document import DocumentMetadata


class KnowledgeService:
    """
    Service d'orchestration du moteur de connaissances.
    """

    def get_connector(
        self,
        source: str,
    ):

        return registry.get(source)

    def discover(
        self,
        source: str,
    ) -> list[DocumentMetadata]:

        connector = self.get_connector(source)

        return connector.discover()

    def discover_all(
        self,
        sources: list[str],
    ) -> list[DocumentMetadata]:

        documents: list[DocumentMetadata] = []

        for source in sources:

            connector = self.get_connector(source)

            documents.extend(
                connector.discover()
            )

        return documents

    def download_attachment(
        self,
        source: str,
        attachment: DocumentAttachment,
    ) -> Path:

        connector = self.get_connector(source)

        return connector.download(
            attachment,
        )

    def download_document(
        self,
        source: str,
        document: DocumentMetadata,
    ) -> list[Path]:

        connector = self.get_connector(source)

        return connector.download_document(
            document,
        )
