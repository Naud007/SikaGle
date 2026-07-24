import requests
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urljoin, urlparse

from app.knowledge_engine.connectors.base import BaseConnector
from app.knowledge_engine.connectors.registry import registry
from app.schemas.document import DocumentMetadata


class FAOConnector(BaseConnector):

    def __init__(self):
        super().__init__("fao")

        # Dépôt officiel de connaissances de la FAO
        self.base_url = "https://openknowledge.fao.org"

        # Page d'accueil du dépôt
        self.repository_url = f"{self.base_url}/home"

        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 "
                "(compatible; SikaGle-KnowledgeEngine/1.0)"
            )
        }

    # =========================================================
    # DÉCOUVERTE DES DOCUMENTS
    # =========================================================

    def discover(self):

        self.log(
            "Recherche des documents dans le FAO Knowledge Repository..."
        )

        response = requests.get(
            self.repository_url,
            headers=self.headers,
            timeout=60
        )

        response.raise_for_status()

        self.log(
            f"Statut HTTP : {response.status_code}"
        )

        self.log(
            f"Taille de la réponse : {len(response.text)} caractères"
        )

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        documents = []

        # Parcours des liens présents sur la page
        for link in soup.find_all(
            "a",
            href=True
        ):

            href = link["href"].strip()

            title = link.get_text(
                " ",
                strip=True
            )

            # Ignorer les liens sans titre
            if not title:
                continue

            # Ignorer les liens trop courts
            if len(title) < 10:
                continue

            # Construire une URL absolue
            full_url = urljoin(
                self.base_url,
                href
            )

            # Vérifier que l'URL est HTTP/HTTPS
            parsed_url = urlparse(
                full_url
            )

            if parsed_url.scheme not in (
                "http",
                "https"
            ):
                continue

            # Ne conserver que les liens du dépôt FAO
            if "openknowledge.fao.org" not in full_url:
                continue

            # Ignorer les pages générales
            excluded_words = [
                "home",
                "about",
                "contact",
                "login",
                "register",
                "privacy",
                "terms"
            ]

            url_lower = full_url.lower()

            if any(
                word in url_lower
                for word in excluded_words
            ):
                continue

            # Créer les métadonnées
            try:

                document = DocumentMetadata(
                    title=title,
                    source="FAO",
                    url=full_url,
                    document_type="publication"
                )

                documents.append(
                    document
                )

            except Exception as e:

                self.log(
                    f"⚠️ Document ignoré : {e}"
                )

        # Suppression des doublons
        unique_documents = {}

        for document in documents:

            unique_documents[
                str(document.url)
            ] = document

        documents = list(
            unique_documents.values()
        )

        self.log(
            f"{len(documents)} document(s) découvert(s)."
        )

        # Affichage des 10 premiers
        for document in documents[:10]:

            self.log(
                f"- {document.title} "
                f"→ {document.url}"
            )

        return documents

    # =========================================================
    # TÉLÉCHARGEMENT DU DOCUMENT
    # =========================================================

    def download(
        self,
        document: DocumentMetadata
    ) -> Path:

        self.log(
            f"Analyse du document : "
            f"{document.title}"
        )

        response = requests.get(
            str(document.url),
            headers=self.headers,
            timeout=60
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        pdf_url = None

        # Recherche d'un lien PDF
        for link in soup.find_all(
            "a",
            href=True
        ):

            href = link["href"].strip()

            full_url = urljoin(
                str(document.url),
                href
            )

            if ".pdf" in full_url.lower():

                pdf_url = full_url

                break

        # Aucun PDF trouvé
        if not pdf_url:

            self.log(
                f"⚠️ Aucun PDF trouvé pour : "
                f"{document.title}"
            )

            return None

        self.log(
            f"PDF trouvé : {pdf_url}"
        )

        # Création d'un nom de fichier propre
        safe_name = "".join(
            character
            if character.isalnum()
            or character in (
                " ",
                "-",
                "_"
            )
            else "_"

            for character
            in document.title
        ).strip()

        # Limiter la longueur
        safe_name = safe_name[:150]

        filename = (
            self.storage_dir
            / f"{safe_name}.pdf"
        )

        # Téléchargement du PDF
        pdf_response = requests.get(
            pdf_url,
            headers=self.headers,
            timeout=120
        )

        pdf_response.raise_for_status()

        # Vérification du contenu
        content_type = (
            pdf_response
            .headers
            .get(
                "content-type",
                ""
            )
            .lower()
        )

        if (
            "pdf" not in content_type
            and not pdf_url.lower().endswith(
                ".pdf"
            )
        ):

            self.log(
                "⚠️ Le fichier téléchargé "
                "ne semble pas être un PDF."
            )

            return None

        # Sauvegarde
        with open(
            filename,
            "wb"
        ) as file:

            file.write(
                pdf_response.content
            )

        self.log(
            f"✅ PDF téléchargé : "
            f"{filename}"
        )

        return filename


# =============================================================
# ENREGISTREMENT DU CONNECTEUR
# =============================================================

registry.register(
    "fao",
    FAOConnector
)
