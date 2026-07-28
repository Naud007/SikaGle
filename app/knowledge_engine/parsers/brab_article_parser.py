from __future__ import annotations

from urllib.parse import urljoin

from bs4 import BeautifulSoup

from app.knowledge_engine.models import BRABArticle


class BRABArticleParser:
    """
    Analyse une page d'un numéro du BRAB
    et extrait les articles.
    """

    BASE_URL = "https://brab.bj"

    def parse(
        self,
        soup: BeautifulSoup,
    ) -> list[BRABArticle]:

        articles: list[BRABArticle] = []

        for link in soup.find_all("a", href=True):

            href = link.get("href")

            if not href:
                continue

            if "/article/view/" not in href:
                continue

            title = link.get_text(
                " ",
                strip=True,
            )

            article = BRABArticle(
                title=title,
                detail_url=urljoin(
                    self.BASE_URL,
                    href,
                ),
            )

            articles.append(article)

        return articles
