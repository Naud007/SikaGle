from __future__ import annotations

from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


class OJSPDFResolver:
    """
    Résout le véritable lien de téléchargement d'un document OJS.

    Fonctionnement BRAB :

        /article/view/{article_id}
                ↓
        a.obj_galley_link
                ↓
        /article/view/{article_id}/{galley_id}
                ↓
        a.download
                ↓
        /article/download/{article_id}/{galley_id}/{file_id}
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
        Inspecte une page OJS et retourne
        les informations utiles sur ses galleys.
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
        # GALLERY LINKS
        # ==================================================

        galley_links = []

        for link in soup.select(
            "a.obj_galley_link[href]"
        ):

            href = urljoin(
                article_url,
                link["href"],
            )

            text = link.get_text(
                " ",
                strip=True,
            )

            galley_links.append(
                {
                    "text": text,
                    "href": href,
                }
            )

            print(
                "GALLEY LINK =",
                text,
                "=>",
                href,
            )

        # ==================================================
        # DOWNLOAD LINKS DIRECTS
        # ==================================================

        download_links = []

        for link in soup.select(
            "a.download[href]"
        ):

            href = urljoin(
                article_url,
                link["href"],
            )

            text = link.get_text(
                " ",
                strip=True,
            )

            download_links.append(
                {
                    "text": text,
                    "href": href,
                }
            )

            print(
                "DOWNLOAD LINK =",
                text,
                "=>",
                href,
            )

        return {
            "article_url": article_url,
            "title": (
                soup.title.text
                if soup.title
                else None
            ),
            "galley_links": galley_links,
            "download_links": download_links,
        }

    def resolve(
        self,
        article_url: str,
    ) -> str | None:
        """
        Résout le véritable lien de téléchargement
        d'un document OJS.
        """

        # ==================================================
        # ÉTAPE 1
        # Ouvrir la page principale de l'article
        # ==================================================

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
        # ÉTAPE 2
        # Chercher les galleys OJS
        # ==================================================

        galley_links = soup.select(
            "a.obj_galley_link[href]"
        )

        if not galley_links:

            print(
                "NO GALLEY LINK FOUND =",
                article_url,
            )

            return None

        print(
            "GALLEYS FOUND =",
            len(galley_links),
        )

        # ==================================================
        # ÉTAPE 3
        # Parcourir les galleys
        # ==================================================

        for galley_link in galley_links:

            galley_url = urljoin(
                article_url,
                galley_link["href"],
            )

            galley_text = galley_link.get_text(
                " ",
                strip=True,
            )

            print(
                "CHECK GALLEY =",
                galley_text,
                "=>",
                galley_url,
            )

            try:

                galley_response = self.session.get(
                    galley_url,
                    timeout=60,
                )

                galley_response.raise_for_status()

            except requests.RequestException as exc:

                print(
                    "GALLEY ERROR =",
                    galley_url,
                    "=>",
                    exc,
                )

                continue

            galley_soup = BeautifulSoup(
                galley_response.text,
                "html.parser",
            )

            # ==================================================
            # ÉTAPE 4
            # Chercher le vrai bouton Télécharger
            # ==================================================

            download_links = galley_soup.select(
                "a.download[href]"
            )

            for download_link in download_links:

                download_url = urljoin(
                    galley_url,
                    download_link["href"],
                )

                print(
                    "RESOLVED DOWNLOAD =",
                    download_url,
                )

                return download_url

        # ==================================================
        # AUCUN FICHIER TROUVÉ
        # ==================================================

        print(
            "NO DOWNLOAD LINK FOUND =",
            article_url,
        )

        return None