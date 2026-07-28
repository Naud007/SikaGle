from __future__ import annotations

from urllib.parse import urljoin

from app.knowledge_engine.models import INRABPublication

from .base_crawler import BaseCrawler


class INRABCrawler(BaseCrawler[INRABPublication]):
    """
    Crawler du portail des publications INRAB.
    """

    BASE_URL = "https://publications-chercheurs.inrab.bj"

    SEARCH_URL = (
        "https://publications-chercheurs.inrab.bj/publications/recherche_simple"
    )

    def discover(self) -> list[INRABPublication]:
        """
        Découvre les publications présentes sur la première page
        du portail INRAB.
        """

        soup = self.fetch(self.SEARCH_URL)

        publications: list[INRABPublication] = []

        # Tous les liens "Lire les détails"
        detail_links = soup.find_all(
            "a",
            string=lambda text: text and "Lire les détails" in text,
        )

        for link in detail_links:

            href = link.get("href")

            if not href:
                continue

            detail_url = urljoin(self.BASE_URL, href)

            card = link.parent

            title = ""

            authors = None

            if card:

                headings = card.find_all(["h3", "h4", "h5"])

                if headings:
                    title = headings[0].get_text(" ", strip=True)

                author_text = card.get_text(" ", strip=True)

                if "Auteur" in author_text:
                    authors = (
                        author_text
                        .split("Auteur:", 1)[-1]
                        .split("Lire les détails")[0]
                        .strip()
                    )

            publications.append(
                INRABPublication(
                    title=title,
                    authors=authors,
                    detail_url=detail_url,
                )
            )

        return publications
