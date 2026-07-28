from __future__ import annotations

from bs4 import BeautifulSoup

from app.knowledge_engine.models import INRABPublication


class INRABPublicationParser:
    """
    Transforme une page HTML INRAB en INRABPublication.
    """

    def parse(
        self,
        soup: BeautifulSoup,
        detail_url: str,
    ) -> INRABPublication:

        title = ""

        title_tag = soup.find(["h1", "h2"])

        if title_tag:
            title = title_tag.get_text(strip=True)

        return INRABPublication(
            title=title,
            detail_url=detail_url,
        )
