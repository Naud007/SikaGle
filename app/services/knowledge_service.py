from __future__ import annotations

from pathlib import Path

from app.knowledge_engine.connectors.registry import registry
from app.knowledge_engine.indexing import KnowledgeIndexer
from app.knowledge_engine.rag import RAGService
from app.schemas.attachment import DocumentAttachment
from app.schemas.document import DocumentMetadata


class KnowledgeService:
    """
    Service principal du moteur de connaissances.

    Il orchestre :
    - les connecteurs de documents ;
    - l'indexation ;
    - le moteur RAG.
    """

    def __init__(self):

        self.indexer = KnowledgeIndexer()

        self.rag = RAGService()

    # ------------------------------------------------------------------
    # Connecteurs
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Indexation
    # ------------------------------------------------------------------

    def index_pdf(
        self,
        pdf_path: Path,
        metadata: dict | None = None,
    ) -> dict:

        return self.indexer.index_pdf(
            pdf_path=pdf_path,
            metadata=metadata,
        )

    # ------------------------------------------------------------------
    # Questions / Réponses
    # ------------------------------------------------------------------

    def ask(
        self,
        question: str,
        top_k: int = 5,
    ) -> dict:

        return self.rag.ask(
            question=question,
            top_k=top_k,
        )
