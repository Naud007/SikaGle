from __future__ import annotations

from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


class OJSPDFResolver:
    """
    Résout automatiquement le véritable lien de téléchargement
    d'un document OJS.
    """

    def __init__(self):

        self.session = requests.Session()

        self.session.headers.update(
            {
                "User-Agent": (
                    "SikaGle Knowledge Engine"
                )
            }
        )

    def inspect(
        self,
        article_url: str,
    ) -> dict:
        """
        Inspecte la page OJS et retourne
        tous les liens présents.
        """

        response = self.session.get(
            article_url,
            timeout=60,
        )

        response.raise_for_status()

        print(
            "HTML CONTAINS DOWNLOAD =",
            "/article/download/" in response.text,
        )

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        # ==================================================
        # LIENS DE TÉLÉCHARGEMENT OJS
        # ==================================================

        download_links = soup.select(
            "a.download[href]"
        )

        for download_link in download_links:

            href = urljoin(
                article_url,
                download_link["href"],
            )

            print(
                "DOWNLOAD LINK =",
                href,
            )

        # ==================================================
        # TOUS LES LIENS
        # ==================================================

        links = []

        for link in soup.find_all(
            "a",
            href=True,
        ):

            href = urljoin(
                article_url,
                link["href"],
            )

            text = link.get_text(
                " ",
                strip=True,
            )

            links.append(
                {
                    "text": text,
                    "href": href,
                }
            )

        return {
            "article_url": article_url,
            "title": (
                soup.title.text
                if soup.title
                else None
            ),
            "links": links,
        }

    def resolve(
        self,
        article_url: str,
    ) -> str | None:
        """
        Recherche le véritable lien de téléchargement
        d'un document OJS.
        """

        response = self.session.get(
            article_url,
            timeout=60,
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        # ==================================================
        # PRIORITÉ 1
        # Lien OJS officiel de téléchargement
        # ==================================================

        download_links = soup.select(
            "a.download[href]"
        )

        for download_link in download_links:

            href = urljoin(
                article_url,
                download_link["href"],
            )

            print(
                "RESOLVED DOWNLOAD =",
                href,
            )

            return href

        # ==================================================
        # PRIORITÉ 2
        # Sécurité : chercher un lien /article/download/
        # ==================================================

        for link in soup.find_all(
            "a",
            href=True,
        ):

            href = urljoin(
                article_url,
                link["href"],
            )

            if "/article/download/" in href.lower():

                print(
                    "RESOLVED DOWNLOAD =",
                    href,
                )

                return href

        # ==================================================
        # AUCUN DOCUMENT DE TÉLÉCHARGEMENT
        # ==================================================

        print(
            "NO DOWNLOAD LINK FOUND =",
            article_url,
        )

        return None