from __future__ import annotations

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
        Sera implémenté lors de la prochaine étape.
        """

        return []
