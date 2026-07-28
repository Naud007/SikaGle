from pathlib import Path

from app.knowledge_engine.connectors.base import BaseConnector
from app.knowledge_engine.crawlers import INRABCrawler
from app.knowledge_engine.normalizers.inrab_normalizer import (
    INRABNormalizer,
)
from app.schemas.document import DocumentMetadata


class INRABConnector(BaseConnector):
    """
    Connecteur du portail INRAB.
    """

    def __init__(self):
        super().__init__("inrab")

        self.crawler = INRABCrawler()
        self.normalizer = INRABNormalizer()

    def discover(self) -> list[DocumentMetadata]:
        """
        Découvre les publications et les transforme
        en DocumentMetadata.
        """

        publications = self.crawler.discover()

        return [
            self.normalizer.normalize(pub)
            for pub in publications
        ]

    def download(self, document: DocumentMetadata) -> Path:
        raise NotImplementedError(
            "Téléchargement INRAB non implémenté."
        )
