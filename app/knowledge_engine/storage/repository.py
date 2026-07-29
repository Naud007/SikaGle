from __future__ import annotations

from abc import ABC, abstractmethod

from app.schemas.document import DocumentMetadata


class KnowledgeRepository(ABC):
    """
    Interface de persistance des documents.
    """

    @abstractmethod
    def save(
        self,
        document: DocumentMetadata,
    ) -> int:
        """
        Enregistre un document.

        Retourne l'identifiant SQLite.
        """
        raise NotImplementedError

    @abstractmethod
    def save_many(
        self,
        documents: list[DocumentMetadata],
    ) -> list[int]:
        """
        Enregistre plusieurs documents.

        Retourne les identifiants SQLite créés.
        """
        raise NotImplementedError

    @abstractmethod
    def get(
        self,
        document_id: int,
    ) -> DocumentMetadata | None:
        """
        Retourne un document à partir de son identifiant.
        """
        raise NotImplementedError

    @abstractmethod
    def list(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[DocumentMetadata]:
        """
        Liste les documents.
        """
        raise NotImplementedError

    @abstractmethod
    def search(
        self,
        query: str,
        limit: int = 50,
    ) -> list[DocumentMetadata]:
        """
        Recherche des documents.
        """
        raise NotImplementedError

    @abstractmethod
    def delete(
        self,
        document_id: int,
    ) -> None:
        """
        Supprime un document.
        """
        raise NotImplementedError

    @abstractmethod
    def count(
        self,
    ) -> int:
        """
        Retourne le nombre total de documents.
        """
        raise NotImplementedError
