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

        self.page_url = (
            "https://www.fao.org/agris/agris-ods"
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
            "[FAO ODS] Analyse de la page "
            "FAO AGRIS ODS..."
        )

        response = requests.get(
            self.page_url,
            headers=self.headers,
            timeout=120
        )

        print(
            "[FAO ODS] Statut HTTP :",
            response.status_code
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
                self.page_url,
                href
            )

            text_lower = text.lower()
            url_lower = full_url.lower()

            # On cherche les liens qui semblent
            # correspondre à un téléchargement
            keywords = [
                "download",
                "ods",
                "xml",
                "rdf",
                "zip",
                "csv",
                "data",
                "dataset"
            ]

            is_candidate = any(
                keyword in text_lower
                or keyword in url_lower
                for keyword in keywords
            )

            if is_candidate:

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
            "[FAO ODS] Liens potentiels :",
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
                "[FAO ODS] ⚠️ Aucun lien "
                "de téléchargement trouvé."
            )

            return None

        print(
            "[FAO ODS] Analyse terminée."
        )

        return links


def test_fao_ods():

    print("=" * 50)

    print(
        "SikaGlé - Test FAO AGRIS ODS"
    )

    print("=" * 50)

    downloader = FAOODSDownloader()

    try:

        links = downloader.download()

        if links:

            print(
                "✅ Liens trouvés :",
                len(links)
            )

            return {
                "status": "success",
                "links": links
            }

        print(
            "⚠️ Aucun lien trouvé."
        )

        return {
            "status": "warning"
        }

    except Exception as e:

        print(
            "❌ Erreur FAO AGRIS ODS :",
            e
        )

        return {
            "status": "error",
            "message": str(e)
        }
