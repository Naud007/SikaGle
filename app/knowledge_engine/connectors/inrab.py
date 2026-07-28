from pathlib import Path

from app.knowledge_engine.connectors.base import BaseConnector
from app.knowledge_engine.connectors.registry import registry
from app.knowledge_engine.crawlers import INRABCrawler
from app.knowledge_engine.normalizers.inrab_normalizer import INRABNormalizer
from app.schemas.document import DocumentMetadata


class INRABConnector(BaseConnector):
    """
    Connecteur du portail des publications INRAB.
    """

    def __init__(self):
        super().__init__("inrab")

        self.crawler = INRABCrawler()
        self.normalizer = INRABNormalizer()

    def discover(self) -> list[DocumentMetadata]:
        """
        Découvre les publications INRAB et les convertit
        en DocumentMetadata.
        """

        publications = self.crawler.discover()

        documents: list[DocumentMetadata] = []

        for publication in publications:
            documents.append(
                self.normalizer.normalize(publication)
            )

        self.log(f"{len(documents)} publications découvertes.")

        return documents

    def download(self, document: DocumentMetadata) -> Path:
        """
        Le téléchargement des PDF sera implémenté
        dans un prochain sprint.
        """
        raise NotImplementedError(
            "Téléchargement INRAB non implémenté."
        )


registry.register("inrab", INRABConnector)
