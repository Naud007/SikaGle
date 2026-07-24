from abc import ABC, abstractmethod
from pathlib import Path

from app.knowledge_engine.config import config


class BaseConnector(ABC):
    """
    Classe de base pour tous les connecteurs du Knowledge Engine.

    Chaque connecteur (FAO, INRAB, BRAB...) devra hériter de cette classe
    et implémenter les méthodes abstraites.
    """

    def __init__(self, source_name: str):
        self.source_name = source_name

        # Dossier où seront enregistrés les documents de cette source
        self.storage_dir = config.raw_dir / source_name
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def discover(self):
        """
        Recherche les nouveaux documents disponibles.

        Retour attendu :
        [
            {
                "title": "...",
                "url": "...",
                "published_at": "..."
            }
        ]
        """
        pass

    @abstractmethod
    def download(self, document: dict):
        """
        Télécharge un document.

        Retour :
        Path vers le PDF téléchargé.
        """
        pass

    def log(self, message: str):
        """
        Affichage standardisé des logs.
        """
        print(f"[{self.source_name.upper()}] {message}")
