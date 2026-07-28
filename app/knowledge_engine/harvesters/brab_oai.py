from __future__ import annotations

from app.knowledge_engine.harvesters.base_oai import (
    BaseOAIHarvester,
)


class BRABOAIHarvester(BaseOAIHarvester):
    """
    Harvester OAI-PMH du BRAB.
    """

    BASE_URL = (
        "https://brab.bj/index.php/brab/oai"
    )

    def __init__(self):
        super().__init__(self.BASE_URL)

    def harvest(self):

        soup = self.fetch(
            {
                "verb": "ListMetadataFormats",
            }
        )

        formats = []

        for metadata in soup.find_all(
            "metadataFormat"
        ):

            prefix = metadata.find(
                "metadataPrefix"
            )

            schema = metadata.find(
                "schema"
            )

            namespace = metadata.find(
                "metadataNamespace"
            )

            formats.append(
                {
                    "prefix": (
                        prefix.text
                        if prefix
                        else None
                    ),
                    "schema": (
                        schema.text
                        if schema
                        else None
                    ),
                    "namespace": (
                        namespace.text
                        if namespace
                        else None
                    ),
                }
            )

        print(
            "[BRAB OAI] "
            f"{len(formats)} format(s) trouvé(s)."
        )

        for fmt in formats:

            print(
                f"- {fmt['prefix']}"
            )

        return formats
