from __future__ import annotations

from urllib.parse import urljoin

from bs4 import BeautifulSoup


class BRABIssueParser:
    """
    Analyse la page des archives du BRAB et extrait
    les liens vers les différents numéros.
    """

    BASE_URL = "https://brab.bj"

    def parse(
        self,
        soup: BeautifulSoup,
    ) -> list[dict]:

        issues: list[dict] = []

        for link in soup.find_all("a", href=True):

            href = link["href"]

            if "/issue/view/" not in href:
                continue

            issues.append(
                {
                    "title": link.get_text(
                        " ",
                        strip=True,
                    ),
                    "url": urljoin(
                        self.BASE_URL,
                        href,
                    ),
                }
            )

        return issues
