import requests
from bs4 import BeautifulSoup

from app.knowledge_engine.config import config


class FAOODSDownloader:

    def __init__(self):

        self.source_name = "fao_agr_is_ods"

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
            "https://www.fao.org/agris/"
        )

    def find_ods_links(self):

        print(
            "[FAO ODS] Recherche des liens ODS..."
        )

        response = requests.get(
            self.page_url,
            timeout=120,
            headers={
                "User-Agent":
                "Mozilla/5.0 "
                "(compatible; "
                "SikaGle-KnowledgeEngine/1.0)"
            }
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

            href = link["href"]

            text = link.get_text(
                " ",
                strip=True
            )

            href_lower = href.lower()
            text_lower = text.lower()

            if (
                "ods" in href_lower
                or "ods" in text_lower
                or "open data" in text_lower
                or "download" in text_lower
            ):

                if href.startswith("/"):

                    href = (
                        "https://www.fao.org"
                        + href
                    )

                elif href.startswith("./"):

                    href = (
                        "https://www.fao.org/agris/"
                        + href[2:]
                    )

                links.append(
                    {
                        "text": text,
                        "url": href
                    }
                )

        print(
            "[FAO ODS] Liens potentiels trouvés :",
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

        links = self.find_ods_links()

        if not links:

            print(
                "[FAO ODS] ⚠️ Aucun lien ODS "
                "trouvé automatiquement."
            )

            return None

        print(
            "[FAO ODS] Un lien potentiel "
            "a été trouvé."
        )

        return links


def test_fao_ods():

    downloader = FAOODSDownloader()

    try:

        links = downloader.download()

        if links:

            print(
                "✅ Liens AGRIS trouvés :",
                len(links)
            )

            return {
                "status": "success",
                "links": links
            }

        else:

            print(
                "⚠️ Aucun lien ODS trouvé."
            )

            return {
                "status": "warning",
                "message":
                    "Aucun lien ODS trouvé"
            }

    except Exception as e:

        print(
            "❌ Erreur FAO AGRIS :",
            e
        )

        return {
            "status": "error",
            "message": str(e)
        }
