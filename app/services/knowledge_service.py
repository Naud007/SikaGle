from __future__ import annotations

from pathlib import Path

from app.knowledge_engine.connectors.registry import registry
from app.knowledge_engine.processing import DocumentProcessor
from app.schemas.attachment import DocumentAttachment
from app.schemas.document import DocumentMetadata


class KnowledgeService:

    def __init__(self):

        self.processor = DocumentProcessor()

    def get_connector(
        self,
        source: str,
    ):

        return registry.get(source)

    def discover(
        self,
        source: str,
    ) -> list[DocumentMetadata]:

        return self.get_connector(
            source
        ).discover()

    def discover_all(
        self,
        sources: list[str],
    ) -> list[DocumentMetadata]:

        documents = []

        for source in sources:

            documents.extend(
                self.discover(source)
            )

        return documents

    def download_attachment(
        self,
        source: str,
        attachment: DocumentAttachment,
    ) -> Path:

        return self.get_connector(
            source
        ).download(
            attachment
        )

    def download_document(
        self,
        source: str,
        document: DocumentMetadata,
    ) -> list[Path]:

        return self.get_connector(
            source
        ).download_document(
            document
        )

    def process_pdf(
        self,
        pdf_path: Path,
    ) -> dict:

        return self.processor.process(
            pdf_path
        )
