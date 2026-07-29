from pathlib import Path

from app.knowledge_engine.embeddings.embedding_service import (
    GeminiEmbeddingService,
)
from app.knowledge_engine.processing import (
    DocumentProcessor,
)
from app.knowledge_engine.vectorstore import (
    ChromaStore,
)


class KnowledgeIndexer:
    """
    Orchestre l'indexation complète d'un document.
    """

    def __init__(self):

        self.processor = DocumentProcessor()

        self.embedding_service = (
            GeminiEmbeddingService()
        )

        self.vectorstore = ChromaStore()

    def index_pdf(
        self,
        pdf_path: Path,
        metadata: dict | None = None,
    ) -> dict:

        metadata = metadata or {}

        result = self.processor.process(
            pdf_path
        )

        chunks = result["chunks"]

        embeddings = []

        for chunk in chunks:

            embeddings.append(
                self.embedding_service.generate_document_embedding(
                    chunk
                )
            )

        self.vectorstore.add_document(
            doc_id=pdf_path.stem,
            chunks=chunks,
            embeddings=embeddings,
            metadata=metadata,
        )

        return {
            "txt_path": result["txt_path"],
            "characters": result["characters"],
            "chunks": result["chunks_count"],
            "indexed": len(chunks),
            "collection_size": self.vectorstore.count(),
        }
