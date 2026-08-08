from __future__ import annotations

from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


class OJSPDFResolver:
    """
    Résout automatiquement le véritable lien PDF
    d'un article OJS.
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
        Retourne tous les liens présents sur la page.
        """

        response = self.session.get(
            article_url,
            timeout=60,
        )

        response.raise_for_status()
        
        print("HTML CONTAINS DOWNLOAD =", "/article/download/" in response.text)

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

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
            "title": soup.title.text if soup.title else None,
            "links": links,
        }

    def resolve(
        self,
        article_url: str,
    ) -> str | None:
        """
        Recherche automatiquement le lien PDF.
        """

        debug = self.inspect(
            article_url
        )

        for link in debug["links"]:
            
            print("LINK:", link["text"], "=>", link["href"])

            href = link["href"].lower()

            text = link["text"].lower()

            if (
                "/article/download/" in href
                or href.endswith(".pdf")
                or "pdf" in text
            ):

                return link["href"]

        return None
