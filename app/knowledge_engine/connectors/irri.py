from __future__ import annotations

from app.knowledge_engine.connectors.base import BaseConnector
from app.knowledge_engine.connectors.registry import registry
from app.knowledge_engine.protocols.oai.client import OAIClient
from app.knowledge_engine.protocols.oai.normalizer import OAINormalizer
from app.knowledge_engine.protocols.oai.parser import OAIParser
from app.schemas.document import DocumentMetadata


class IRRIConnector(BaseConnector):
    """
    Connecteur OAI-PMH pour la collection IRRI (International
    Rice Research Institute), hébergée sur Harvard Dataverse.

    NOTE (licence, 31/08/2026) : contrairement à AfricaRice,
    IRRI n'a PAS de licence unique garantie pour tout son
    dépôt — chaque dataset est licencié individuellement par
    son auteur (confirmé : au moins un dataset en CC BY-NC,
    non-commercial). C'est pour cela que "irri" figure dans
    OAIIngestionWorker.SOURCES_REQUIRING_LICENSE_CHECK, qui
    vérifie la licence réelle de chaque document via
    DataverseLicenseChecker avant ingestion — ne jamais
    retirer cette source de cette liste sans revérifier.
    """

    BASE_URL = "https://dataverse.harvard.edu/oai"

    OAI_SET = "IRRI"

    def __init__(self):
        super().__init__("irri")

        self.client = OAIClient(self.BASE_URL)
        self.parser = OAIParser()
        self.normalizer = OAINormalizer()

    def discover(
        self,
    ) -> list[DocumentMetadata]:

        documents: list[DocumentMetadata] = []

        soup = self.client.list_records(
            set_spec=self.OAI_SET
        )

        while True:

            records = self.parser.parse_records(soup)

            for record in records:

                documents.append(
                    self.normalizer.normalize(
                        record,
                        source="IRRI",
                    )
                )

            token = self.parser.parse_resumption_token(
                soup
            )

            if token is None:
                break

            soup = self.client.list_records_from_token(
                token
            )

        return documents


registry.register(
    "irri",
    IRRIConnector,
)