from __future__ import annotations

from app.knowledge_engine.models import BRABArticle

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

    def discover(self) -> list[BRABArticle]:
        """
        Découvre les numéros du BRAB.

        Le parsing des archives sera implémenté
        à l'étape suivante.
        """

        soup = self.fetch(self.ARCHIVES_URL)

        self.log(
            "Archives BRAB récupérées avec succès."
        )

        return []
