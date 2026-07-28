from __future__ import annotations

from app.knowledge_engine.models import BRABArticle
from app.knowledge_engine.parsers.brab_article_parser import (
    BRABArticleParser,
)
from app.knowledge_engine.parsers.brab_issue_parser import (
    BRABIssueParser,
)

from .base_crawler import BaseCrawler


class BRABCrawler(BaseCrawler[BRABArticle]):
    """
    Crawler du Bulletin de la Recherche Agronomique
    du Bénin (BRAB).
    """

    BASE_URL = "https://brab.bj"

    ARCHIVES_URL = (
        "https://brab.bj/index.php/brab/issue/archive"
    )

    def __init__(self):
        super().__init__()

        self.issue_parser = BRABIssueParser()
        self.article_parser = BRABArticleParser()

    def discover(self) -> list[BRABArticle]:
        """
        Découvre tous les articles disponibles
        dans les archives du BRAB.
        """

        archive_soup = self.fetch(
            self.ARCHIVES_URL
        )

        issues = self.issue_parser.parse(
            archive_soup
        )

        self.log(
            f"{len(issues)} numéro(s) trouvé(s)."
        )

        articles: list[BRABArticle] = []

        for issue in issues:

            try:

                issue_soup = self.fetch(
                    issue["url"]
                )

                issue_articles = (
                    self.article_parser.parse(
                        self,
                        issue_soup,
                    )
                )

                articles.extend(
                    issue_articles
                )

                self.log(
                    f"{issue['title']} : "
                    f"{len(issue_articles)} article(s)"
                )

            except Exception as exc:

                self.log(
                    f"Erreur sur {issue['url']} : "
                    f"{exc}"
                )

        self.log(
            f"{len(articles)} article(s) découvert(s)."
        )

        return articles
