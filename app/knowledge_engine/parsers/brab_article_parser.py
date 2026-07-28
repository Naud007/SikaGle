from __future__ import annotations

from urllib.parse import urljoin

from bs4 import BeautifulSoup

from app.knowledge_engine.models import BRABArticle
from app.knowledge_engine.parsers.brab_publication_parser import (
    BRABPublicationParser,
)


class BRABArticleParser:
    """
    Analyse un numéro du BRAB et extrait
    les articles.
    """

    BASE_URL = "https://brab.bj"

    def __init__(self):
        self.publication_parser = (
            BRABPublicationParser()
        )

    def parse(
        self,
        crawler,
        soup: BeautifulSoup,
    ) -> list[BRABArticle]:

        articles: list[BRABArticle] = []

        for link in soup.find_all(
            "a",
            href=True,
        ):

            href = link.get("href")

            if not href:
                continue

            if "/article/view/" not in href:
                continue

            detail_url = urljoin(
                self.BASE_URL,
                href,
            )

            try:

                detail_soup = crawler.fetch(
                    detail_url
                )

                article = (
                    self.publication_parser.parse(
                        detail_soup,
                        detail_url,
                    )
                )

                articles.append(
                    article
                )

            except Exception as exc:

                print(
                    f"Erreur lors de l'analyse de "
                    f"{detail_url}: {exc}"
                )

        return articles
