import requests
from bs4 import BeautifulSoup
from pathlib import Path

from app.knowledge_engine.connectors.base import BaseConnector
from app.knowledge_engine.connectors.registry import registry
from app.schemas.document import DocumentMetadata


class FAOConnector(BaseConnector):

    def __init__(self):
        super().__init__("fao")

    def discover(self):
        self.log("Recherche des nouveaux documents FAO...")

        # Temporaire (sera remplacé par le scraping/API)
        return [
            DocumentMetadata(
                title="Guide de production du maïs",
                source="FAO",
                url="https://www.fao.org/3/example.pdf",
                crop="Maïs",
            )
        ]

    def download(self, document: DocumentMetadata) -> Path:
        self.log(f"Téléchargement : {document.title}")

        filename = self.storage_dir / "example.pdf"

        filename.touch(exist_ok=True)

        return filename


registry.register("fao", FAOConnector)
