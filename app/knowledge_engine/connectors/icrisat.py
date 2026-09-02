from __future__ import annotations

from app.knowledge_engine.connectors.base import BaseConnector
from app.knowledge_engine.connectors.registry import registry
from app.knowledge_engine.protocols.oai.client import OAIClient
from app.knowledge_engine.protocols.oai.normalizer import OAINormalizer
from app.knowledge_engine.protocols.oai.parser import OAIParser
from app.schemas.document import DocumentMetadata


class ICRISATConnector(BaseConnector):
    """
    Connecteur OAI-PMH pour ICRISAT (International Crops
    Research Institute for the Semi-Arid Tropics), hébergé
    sur SA PROPRE instance Dataverse — contrairement à
    AfricaRice/IRRI/CIFOR/Bioversity qui partagent tous
    Harvard Dataverse, ICRISAT a son propre serveur
    (dataverse.icrisat.org), donc pas de filtre "set" requis
    (toute l'instance appartient à ICRISAT).

    NOTE (licence, 01/09/2026) : licence affichée comme "CC"
    générique sur re3data, sans précision BY/NC/SA — ambiguë,
    comme IRRI/CIFOR. C'est pour cela que "icrisat" figure
    dans OAIIngestionWorker.SOURCES_REQUIRING_LICENSE_CHECK,
    avec un DataverseLicenseChecker pointé vers l'API native
    d'ICRISAT (pas celle de Harvard).
    """

    BASE_URL = "https://dataverse.icrisat.org/oai"

    def __init__(self):
        super().__init__("icrisat")

        self.client = OAIClient(self.BASE_URL)
        self.parser = OAIParser()
        self.normalizer = OAINormalizer()

    def discover(
        self,
    ) -> list[DocumentMetadata]:
        """
        Découvre tous les documents disponibles via OAI-PMH.
        Pas de filtre "set" : toute l'instance ICRISAT est
        pertinente, contrairement à Harvard Dataverse qui
        héberge des centaines d'institutions différentes.
        """

        documents: list[DocumentMetadata] = []

        soup = self.client.list_records()

        while True:

            records = self.parser.parse_records(soup)

            for record in records:

                documents.append(
                    self.normalizer.normalize(
                        record,
                        source="ICRISAT",
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
    "icrisat",
    ICRISATConnector,
)