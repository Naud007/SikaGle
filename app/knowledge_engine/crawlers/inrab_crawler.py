from __future__ import annotations

from urllib.parse import urljoin

from app.knowledge_engine.models import INRABPublication
from app.knowledge_engine.parsers.inrab_publication_parser import (
    INRABPublicationParser,
)

from .base_crawler import BaseCrawler


class INRABCrawler(BaseCrawler[INRABPublication]):
    """
    Crawler du portail des publications INRAB.
    """

    BASE_URL = "https://publications-chercheurs.inrab.bj"

    SEARCH_URL = (
        "https://publications-chercheurs.inrab.bj/publications/recherche_simple"
    )

    def __init__(self):
        super().__init__()
        self.parser = INRABPublicationParser()

    def discover(self) -> list[INRABPublication]:
        """
        Découvre les publications disponibles.
        """

        soup = self.fetch(self.SEARCH_URL)

        publications: list[INRABPublication] = []

        detail_links = soup.find_all(
            "a",
            string=lambda text: text and "Lire les détails" in text,
        )

        for link in detail_links:

            href = link.get("href")

            if not href:
                continue

            detail_url = urljoin(self.BASE_URL, href)

            try:
                detail_soup = self.fetch(detail_url)

                publication = self.parser.parse(
                    detail_soup,
                    detail_url,
                )

                publications.append(publication)

            except Exception as exc:
                print(f"Erreur lors de l'analyse de {detail_url}: {exc}")

        return publications
