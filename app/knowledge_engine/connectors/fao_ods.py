import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from app.knowledge_engine.config import config


class FAOODSDownloader:

    def __init__(self):

        self.source_name = "fao_agris_ods"

        self.download_dir = (
            config.raw_dir
            / "fao"
            / "ods"
        )

        self.download_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.catalog_url = (
            "https://data.apps.fao.org/catalog/dcat/agris"
        )

        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 "
                "(compatible; "
                "SikaGle-KnowledgeEngine/1.0)"
            )
        }

    def find_download_links(self):

        print(
            "[FAO ODS] Accès au catalogue "
            "de données FAO..."
        )

        response = requests.get(
            self.catalog_url,
            headers=self.headers,
            timeout=120
        )

        print(
            "[FAO ODS] Statut HTTP :",
            response.status_code
        )

        print(
            "[FAO ODS] Taille réponse :",
            len(response.content),
            "octets"
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        links = []

        for link in soup.find_all(
            "a",
            href=True
        ):

            href = link["href"].strip()

            text = link.get_text(
                " ",
                strip=True
            )

            full_url = urljoin(
                self.catalog_url,
                href
            )

            links.append(
                {
                    "text": text,
                    "url": full_url
                }
            )

        # Supprimer les doublons
        unique_links = {}

        for link in links:

            unique_links[
                link["url"]
            ] = link

        links = list(
            unique_links.values()
        )

        print(
            "[FAO ODS] Nombre total de liens :",
            len(links)
        )

        for link in links:

            print(
                "[FAO ODS] -",
                link["text"],
                "→",
                link["url"]
            )

        return links

    def download(self):

        links = self.find_download_links()

        if not links:

            print(
                "[FAO ODS] ⚠️ Aucun lien trouvé."
            )

            return None

        print(
            "[FAO ODS] Catalogue analysé."
        )

        return links


def test_fao_ods():

    print("=" * 50)

    print(
        "SikaGlé - Test FAO AGRIS Data Catalog"
    )

    print("=" * 50)

    downloader = FAOODSDownloader()

    try:

        links = downloader.download()

        if links:

            print(
                "✅ Catalogue FAO accessible."
            )

            return {
                "status": "success",
                "links": links
            }

        return {
            "status": "warning",
            "message": "Aucun lien trouvé"
        }

    except Exception as e:

        print(
            "❌ Erreur catalogue FAO :",
            e
        )

        return {
            "status": "error",
            "message": str(e)
        }
