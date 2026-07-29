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

    def resolve(
        self,
        article_url: str,
    ) -> str | None:
        """
        Recherche le lien PDF réel
        depuis la page de l'article.
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

        # Recherche de tous les liens
        for link in soup.find_all(
            "a",
            href=True,
        ):

            href = link["href"]

            text = link.get_text(
                " ",
                strip=True,
            ).lower()

            href_lower = href.lower()

            # Cas classiques OJS
            if (
                "/article/download/" in href_lower
                or href_lower.endswith(".pdf")
                or "pdf" in text
            ):

                return urljoin(
                    article_url,
                    href,
                )

        return None
