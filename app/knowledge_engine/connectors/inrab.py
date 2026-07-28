from pathlib import Path

from app.knowledge_engine.connectors.base import BaseConnector
from app.knowledge_engine.crawlers import INRABCrawler
from app.schemas.document import DocumentMetadata


class INRABConnector(BaseConnector):
    """
    Connecteur du portail INRAB.
    """

    def __init__(self):
        super().__init__("inrab")
        self.crawler = INRABCrawler()

    def discover(self) -> list[DocumentMetadata]:
        """
        Temporaire.
        Le normalizer sera ajouté ensuite.
        """

        return []

    def download(self, document: DocumentMetadata) -> Path:
        """
        Sera implémenté lors du téléchargement des PDF.
        """
        raise NotImplementedError("Téléchargement INRAB non implémenté.")
