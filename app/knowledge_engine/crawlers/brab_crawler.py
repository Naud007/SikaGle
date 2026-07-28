from __future__ import annotations

from app.knowledge_engine.models import BRABArticle
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

    def discover(self) -> list[BRABArticle]:
        """
        Découvre les numéros du BRAB.
        """

        soup = self.fetch(self.ARCHIVES_URL)

        issues = self.issue_parser.parse(soup)

        self.log(
            f"{len(issues)} numéro(s) découvert(s)."
        )

        # Les articles seront extraits
        # à l'étape suivante.
        return []
