from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

import requests
from bs4 import BeautifulSoup

T = TypeVar("T")


class BaseCrawler(ABC, Generic[T]):
    """
    Classe de base pour tous les crawlers du Knowledge Engine.

    Responsabilités :
    - effectuer les requêtes HTTP ;
    - créer un objet BeautifulSoup ;
    - laisser aux classes filles la logique de découverte.
    """

    def __init__(self, timeout: int = 30):
        self.timeout = timeout

        self.session = requests.Session()

        self.session.headers.update(
            {
                "User-Agent": (
                    "SikaGle Knowledge Engine/1.0 "
                    "(https://github.com/Naud007/SikaGle)"
                )
            }
        )

    def fetch(self, url: str) -> BeautifulSoup:
        """
        Télécharge une page HTML et retourne un objet BeautifulSoup.
        """

        response = self.session.get(
            url,
            timeout=self.timeout,
        )

        response.raise_for_status()

        return BeautifulSoup(
            response.text,
            "html.parser",
        )

    @abstractmethod
    def discover(self) -> list[T]:
        """
        Découvre les ressources de la source.
        """
        raise NotImplementedError
