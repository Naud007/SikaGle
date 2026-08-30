from __future__ import annotations

from pathlib import Path

from app.knowledge_engine.connectors.registry import registry
from app.knowledge_engine.debug import DebugService
from app.knowledge_engine.indexing import KnowledgeIndexer
from app.knowledge_engine.ingestion import IngestionManager
from app.knowledge_engine.rag import RAGService
from app.schemas.attachment import DocumentAttachment
from app.schemas.document import DocumentMetadata


class KnowledgeService:
    """
    Service principal du moteur de connaissances.

    Il orchestre :
    - les connecteurs ;
    - l'ingestion ;
    - l'indexation ;
    - le moteur RAG ;
    - les outils de diagnostic.
    """

    def __init__(self):

        self.indexer = KnowledgeIndexer()

        self.ingestion = IngestionManager()

        self.rag = RAGService()

        self.debug = DebugService()

    # ------------------------------------------------------------------
    # Connecteurs
    # ------------------------------------------------------------------

    def get_connector(
        self,
        source: str,
    ):

        return registry.get(source)

    def available_sources(
        self,
    ) -> list[str]:

        return registry.names()

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
    # Ingestion
    # ------------------------------------------------------------------

    def ingest_source(
        self,
        source: str,
        limit: int | None = 5,
        offset: int = 0,
    ):

        return self.ingestion.ingest_source(
            source=source,
            limit=limit,
            offset=offset,
        )

    def ingest_all(
        self,
    ):

        return self.ingestion.ingest_all()

    # ------------------------------------------------------------------
    # Debug
    # ------------------------------------------------------------------

    def debug_pdf(
        self,
        pdf_path: Path,
    ) -> dict:

        return self.debug.inspect_pdf(
            pdf_path
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
        source: str | None = None,
        language: str | None = None,
        input_type: str = "text",
        publication_type: str | None = None,
        publication_year: int | None = None,
        weather_context: str | None = None,
    ) -> dict:

        return self.rag.ask(
            question=question,
            top_k=top_k,
            source=source,
            language=language,
            input_type=input_type,
            publication_type=publication_type,
            publication_year=publication_year,
            weather_context=weather_context,
        )