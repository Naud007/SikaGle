from __future__ import annotations

import requests
from bs4 import BeautifulSoup


class PDFExtractor:
    """
    Extrait l'URL du PDF depuis une page d'article OJS.
    """

    def extract_pdf_url(
        self,
        article_url: str,
    ) -> str | None:

        response = requests.get(
            article_url,
            timeout=30,
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        for link in soup.find_all("a", href=True):

            href = link["href"]

            if "/article/view/" in href and "/pdf" in href:

                if href.startswith("http"):

                    return href

                return (
                    "https://brab.bj"
                    + href
                )

        return None
