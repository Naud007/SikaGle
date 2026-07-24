from abc import ABC, abstractmethod
from pathlib import Path

from app.knowledge_engine.config import config
from app.schemas.document import DocumentMetadata


class BaseConnector(ABC):
    """
    Classe de base pour tous les connecteurs du Knowledge Engine.
    """

    def __init__(self, source_name: str):
        self.source_name = source_name

        # Dossier de stockage propre à chaque source
        self.storage_dir = config.raw_dir / source_name
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def discover(self) -> list[DocumentMetadata]:
        """
        Recherche les documents disponibles auprès de la source.

        Retourne une liste de DocumentMetadata.
        """
        pass

    @abstractmethod
    def download(self, document: DocumentMetadata) -> Path:
        """
        Télécharge un document.

        Retourne le chemin du fichier téléchargé.
        """
        pass

    def log(self, message: str):
        """
        Affichage standardisé des logs.
        """
        print(f"[{self.source_name.upper()}] {message}")
