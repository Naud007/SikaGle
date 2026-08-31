from __future__ import annotations

from app.knowledge_engine.connectors.base import BaseConnector
from app.knowledge_engine.connectors.registry import registry
from app.knowledge_engine.protocols.oai.client import OAIClient
from app.knowledge_engine.protocols.oai.normalizer import OAINormalizer
from app.knowledge_engine.protocols.oai.parser import OAIParser
from app.schemas.document import DocumentMetadata


class AfricaRiceConnector(BaseConnector):
    """
    Connecteur OAI-PMH pour la collection AfricaRice, hébergée
    sur Harvard Dataverse.

    NOTE (licence, 31/08/2026) : la collection AfricaRice est
    en licence CC0 (domaine public), vérifiée avant intégration
    — voir la note dans la mémoire du projet sur le panorama de
    licences des sources documentaires.

    NOTE (contenu) : contrairement à BRAB/FAO AGRIS (articles
    scientifiques), AfricaRice héberge surtout des JEUX DE
    DONNÉES de recherche (agronomie, sélection variétale,
    entomologie, pathologie du riz) — les descriptions de
    méthodologie/contexte de chaque dataset sont ce qui nourrit
    le RAG ici, pas des articles complets.
    """

    BASE_URL = "https://dataverse.harvard.edu/oai"

    OAI_SET = "AfricaRice"

    def __init__(self):
        super().__init__("africarice")

        self.client = OAIClient(self.BASE_URL)
        self.parser = OAIParser()
        self.normalizer = OAINormalizer()

    def discover(
        self,
    ) -> list[DocumentMetadata]:
        """
        Découvre tous les documents disponibles via OAI-PMH,
        filtrés sur la collection AfricaRice uniquement (parmi
        les nombreuses institutions hébergées sur Harvard
        Dataverse).
        """

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
                        source="AfricaRice",
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
    "africarice",
    AfricaRiceConnector,
)