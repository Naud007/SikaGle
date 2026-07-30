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

        # =====================================
        # DOUBLON
        # =====================================

        if self.vectorstore.exists(
            pdf_path.stem
        ):

            return {

                "validated": True,

                "indexed": False,

                "duplicate": True,

                "errors": [],

                "warnings": [
                    "Document déjà indexé."
                ],

                "txt_path": None,

                "characters": 0,

                "chunks": 0,

                "collection_size": self.vectorstore.count(),
            }

        # =====================================
        # TRAITEMENT
        # =====================================

        result = self.processor.process(
            pdf_path
        )

        validation = result[
            "validation"
        ]

        # =====================================
        # VALIDATION
        # =====================================

        if not validation.valid:

            return {

                "validated": False,

                "indexed": False,

                "duplicate": False,

                "errors": validation.errors,

                "warnings": validation.warnings,

                "txt_path": result[
                    "txt_path"
                ],

                "characters": result[
                    "characters"
                ],

                "chunks": result[
                    "chunks_count"
                ],

                "collection_size": self.vectorstore.count(),
            }

        chunks = result["chunks"]

        # =====================================
        # EMBEDDINGS
        # =====================================

        embeddings = []

        for chunk in chunks:

            embeddings.append(
                self.embedding_service.generate_document_embedding(
                    chunk
                )
            )

        # =====================================
        # VECTOR STORE
        # =====================================

        self.vectorstore.add_document(

            doc_id=pdf_path.stem,

            chunks=chunks,

            embeddings=embeddings,

            metadata=metadata,
        )

        # =====================================
        # RAPPORT
        # =====================================

        return {

            "validated": True,

            "indexed": True,

            "duplicate": False,

            "errors": [],

            "warnings": validation.warnings,

            "txt_path": result[
                "txt_path"
            ],

            "characters": result[
                "characters"
            ],

            "chunks": result[
                "chunks_count"
            ],

            "collection_size": self.vectorstore.count(),
        }
