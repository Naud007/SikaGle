from __future__ import annotations

from urllib.parse import urljoin

from bs4 import BeautifulSoup

from app.knowledge_engine.models import INRABPublication


class INRABPublicationParser:
    """
    Transforme une page HTML INRAB en INRABPublication.
    """

    BASE_URL = "https://publications-chercheurs.inrab.bj"

    def parse(
        self,
        soup: BeautifulSoup,
        detail_url: str,
    ) -> INRABPublication:

        # -----------------------------
        # Titre
        # -----------------------------
        title = ""

        title_tag = soup.find(["h1", "h2"])

        if title_tag:
            title = title_tag.get_text(" ", strip=True)

        # -----------------------------
        # PDF
        # -----------------------------
        pdf_url = None

        for link in soup.find_all("a", href=True):

            href = link["href"]

            if href.lower().endswith(".pdf"):
                pdf_url = urljoin(self.BASE_URL, href)
                break

        return INRABPublication(
            title=title,
            detail_url=detail_url,
            pdf_url=pdf_url,
        )
