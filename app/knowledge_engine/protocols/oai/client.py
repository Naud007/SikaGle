from __future__ import annotations

from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup


class OAIClient:
    """
    Client générique pour communiquer avec
    un dépôt OAI-PMH.
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

    def request(
        self,
        **params,
    ) -> BeautifulSoup:
        """
        Envoie une requête OAI-PMH.
        """

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

    def identify(self):

        return self.request(
            verb="Identify"
        )

    def list_metadata_formats(self):

        return self.request(
            verb="ListMetadataFormats"
        )

    def list_sets(self):

        return self.request(
            verb="ListSets"
        )

    def list_identifiers(
        self,
        metadata_prefix="oai_dc",
    ):

        return self.request(
            verb="ListIdentifiers",
            metadataPrefix=metadata_prefix,
        )

    def list_records(
        self,
        metadata_prefix="oai_dc",
    ):

        return self.request(
            verb="ListRecords",
            metadataPrefix=metadata_prefix,
        )

    def get_record(
        self,
        identifier: str,
        metadata_prefix="oai_dc",
    ):

        return self.request(
            verb="GetRecord",
            identifier=identifier,
            metadataPrefix=metadata_prefix,
        )
