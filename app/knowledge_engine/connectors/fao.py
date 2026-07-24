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
        self.log("Recherche des publications FAO...")

        url = "https://www.fao.org/publications/en/"

        response = requests.get(url, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")

        documents = []

        for link in soup.find_all("a", href=True):

            href = link["href"]

            if ".pdf" not in href.lower():
                continue

            title = link.get_text(strip=True)

            if not title:
                title = "Publication FAO"

            if href.startswith("/"):
                href = "https://www.fao.org" + href

            document = DocumentMetadata(
                title=title,
                source="FAO",
                url=href,
                document_type="publication",
            )

            documents.append(document)

        self.log(f"{len(documents)} document(s) PDF trouvé(s).")

        return documents

    def download(self, document: DocumentMetadata) -> Path:
        self.log(f"Téléchargement : {document.title}")

        filename = self.storage_dir / "document.pdf"

        response = requests.get(
            str(document.url),
            timeout=60,
            stream=True,
            headers={
                "User-Agent": "SikaGle-KnowledgeEngine/1.0"
            }
        )

        response.raise_for_status()

        with open(filename, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)

        self.log(f"Document téléchargé : {filename}")

        return filename


registry.register("fao", FAOConnector)
