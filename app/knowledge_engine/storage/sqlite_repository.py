from __future__ import annotations

from app.knowledge_engine.storage.database import database
from app.knowledge_engine.storage.repository import KnowledgeRepository
from app.schemas.document import DocumentMetadata


class SQLiteRepository(KnowledgeRepository):
    """
    Implémentation SQLite du KnowledgeRepository.
    """

    def __init__(self) -> None:
        self.database = database

    def save(
        self,
        document: DocumentMetadata,
    ) -> int:
        """
        Enregistre un document complet.
        """

        existing = self._document_exists(document)

        if existing is not None:
            return existing

        document_id = self._insert_document(document)

        self._insert_authors(
            document_id,
            document,
        )

        self._insert_keywords(
            document_id,
            document,
        )

        self._insert_attachments(
            document_id,
            document,
        )

        self.database.commit()

        return document_id

    def save_many(
        self,
        documents: list[DocumentMetadata],
    ) -> list[int]:
        raise NotImplementedError

    def get(
        self,
        document_id: int,
    ) -> DocumentMetadata | None:
        raise NotImplementedError

    def list(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[DocumentMetadata]:
        raise NotImplementedError

    def search(
        self,
        query: str,
        limit: int = 50,
    ) -> list[DocumentMetadata]:
        raise NotImplementedError

    def delete(
        self,
        document_id: int,
    ) -> None:
        raise NotImplementedError

    def count(
        self,
    ) -> int:

        cursor = self.database.cursor()

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM documents
            """
        )

        return cursor.fetchone()[0]

    # -------------------------------------------------
    # Méthodes privées
    # -------------------------------------------------

    def _document_exists(
        self,
        document: DocumentMetadata,
    ) -> int | None:
        raise NotImplementedError

    def _insert_document(
        self,
        document: DocumentMetadata,
    ) -> int:
        raise NotImplementedError

    def _insert_authors(
        self,
        document_id: int,
        document: DocumentMetadata,
    ) -> None:
        raise NotImplementedError

    def _insert_keywords(
        self,
        document_id: int,
        document: DocumentMetadata,
    ) -> None:
        raise NotImplementedError

    def _insert_attachments(
        self,
        document_id: int,
        document: DocumentMetadata,
    ) -> None:
        raise NotImplementedError
