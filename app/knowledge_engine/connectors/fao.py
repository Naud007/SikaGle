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

        response = requests.get(
            url,
            timeout=30,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")

        documents = []

        # Parcours des liens de la page
        for link in soup.find_all("a", href=True):

            href = link["href"].strip()
            title = link.get_text(" ", strip=True)

            # Ignorer les liens non HTTP
            if not href.startswith(("http://", "https://", "/")):
                continue

            # Ignorer les titres trop courts
            if len(title) < 15:
                continue

            # Construire une URL complète
            if href.startswith("/"):
                href = "https://www.fao.org" + href

            # Garder uniquement les pages de publications
            if "/publications/" not in href:
                continue

            # Exclure les pages générales
            excluded = [
                "/publications/en/",
                "/publications/about-fao-publishing/",
                "/publications/news-archive/",
                "/publications/library/",
                "/publications/wikiproject/",
                "/publications/fao-flagship-publications/",
                "/publications/fao-corporate-brochures/",
            ]

            if any(path in href for path in excluded):
                continue

            documents.append(
                DocumentMetadata(
                    title=title,
                    source="FAO",
                    url=href,
                    document_type="publication",
                )
            )

        # Supprimer les doublons
        unique_documents = {}

        for document in documents:
            unique_documents[document.url] = document

        documents = list(unique_documents.values())

        self.log(
            f"{len(documents)} publication(s) pertinente(s) trouvée(s)."
        )

        for document in documents[:10]:
            self.log(
                f"- {document.title} → {document.url}"
            )

        return documents

    def download(self, document: DocumentMetadata) -> Path:
        self.log(f"Analyse de la page : {document.title}")

        response = requests.get(
            str(document.url),
            timeout=60,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")

        pdf_url = None

        # Recherche d'un lien PDF
        for link in soup.find_all("a", href=True):

            href = link["href"].strip()

            if ".pdf" in href.lower():

                pdf_url = href

                if pdf_url.startswith("/"):
                    pdf_url = "https://www.fao.org" + pdf_url

                break

        if not pdf_url:
            self.log(
                f"⚠️ Aucun PDF trouvé pour : {document.title}"
            )

            return None

        self.log(f"PDF trouvé : {pdf_url}")

        safe_name = "".join(
            c if c.isalnum() or c in (" ", "-", "_") else "_"
            for c in document.title
        ).strip()

        filename = self.storage_dir / f"{safe_name}.pdf"

        pdf_response = requests.get(
            pdf_url,
            timeout=60,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        pdf_response.raise_for_status()

        with open(filename, "wb") as file:
            file.write(pdf_response.content)

        self.log(f"✅ PDF téléchargé : {filename}")

        return filename


registry.register("fao", FAOConnector)
