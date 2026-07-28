from __future__ import annotations

from abc import ABC, abstractmethod

import requests
from bs4 import BeautifulSoup


class BaseOAIHarvester(ABC):
    """
    Classe de base pour tous les harvesters OAI-PMH.
    """

    def __init__(self, base_url: str):
        self.base_url = base_url

        self.session = requests.Session()

        self.session.headers.update(
            {
                "User-Agent": (
                    "SikaGle Knowledge Engine"
                )
            }
        )

    def fetch(
        self,
        params: dict,
    ) -> BeautifulSoup:

        response = self.session.get(
            self.base_url,
            params=params,
            timeout=60,
        )

        response.raise_for_status()

        return BeautifulSoup(
            response.content,
            "xml",
        )

    @abstractmethod
    def harvest(self):
        """
        Lance le moissonnage du dépôt OAI.
        """
        pass
