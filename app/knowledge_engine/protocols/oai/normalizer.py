from __future__ import annotations

from app.knowledge_engine.protocols.oai.record import (
    OAIRecord,
)
from app.schemas.document import DocumentMetadata


class OAINormalizer:
    """
    Transforme un OAIRecord en DocumentMetadata.
    """

    def normalize(
        self,
        record: OAIRecord,
    ) -> DocumentMetadata:

        metadata = record.metadata

        def first(name: str) -> str | None:

            values = metadata.get(name)

            if not values:
                return None

            return values[0]

        return DocumentMetadata(
            identifier=record.identifier,
            title=first("title"),
            abstract=first("description"),
            authors=metadata.get(
                "creator",
                [],
            ),
            keywords=metadata.get(
                "subject",
                [],
            ),
            language=first("language"),
            publication_date=record.datestamp,
            source="oai",
            url=first("identifier"),
        )
