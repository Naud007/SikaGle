from abc import ABC, abstractmethod
from pathlib import Path

from app.knowledge_engine.config import config
from app.schemas.document import DocumentMetadata


class BaseConnector(ABC):
    """
    Classe de base pour tous les connecteurs du Knowledge Engine.
    """

    # Métadonnées du connecteur
    source_name: str = ""
    organization: str = ""
    country: str = ""
    supported_formats: list[str] = []
    supported_document_types: list[str] = []

    def __init__(self):
        if not self.source_name:
            raise ValueError(
                "Chaque connecteur doit définir source_name."
            )

        self.storage_dir = config.raw_dir / self.source_name
        self.storage_dir.mkdir(
            parents=True,
            exist_ok=True
        )

    @abstractmethod
    def discover(self) -> list[DocumentMetadata]:
        """
        Recherche les documents disponibles.
        """
        pass

    @abstractmethod
    def download(
        self,
        document: DocumentMetadata
    ) -> Path:
        """
        Télécharge un document.
        """
        pass

    def capabilities(self) -> dict:
        """
        Retourne les capacités du connecteur.
        """

        return {
            "source": self.source_name,
            "organization": self.organization,
            "country": self.country,
            "formats": self.supported_formats,
            "document_types": self.supported_document_types,
        }

    def log(
        self,
        message: str
    ):
        print(
            f"[{self.source_name.upper()}] {message}"
        )
