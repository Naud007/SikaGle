from __future__ import annotations

from urllib.parse import urljoin

from bs4 import BeautifulSoup

from app.knowledge_engine.models import BRABArticle


class BRABPublicationParser:
    """
    Analyse la page d'un article BRAB.
    """

    BASE_URL = "https://brab.bj"

    def parse(
        self,
        soup: BeautifulSoup,
        detail_url: str,
    ) -> BRABArticle:

        # ----------------------------------
        # Titre
        # ----------------------------------

        title = ""

        title_tag = soup.find("h1")

        if title_tag:
            title = title_tag.get_text(
                " ",
                strip=True,
            )

        # ----------------------------------
        # PDF
        # ----------------------------------

        pdf_url = None

        for link in soup.find_all(
            "a",
            href=True,
        ):

            href = link["href"]

            if "/article/view/" in href and "/pdf" in href:

                pdf_url = urljoin(
                    self.BASE_URL,
                    href,
                )

                break

        return BRABArticle(
            title=title,
            detail_url=detail_url,
            pdf_url=pdf_url,
        )
