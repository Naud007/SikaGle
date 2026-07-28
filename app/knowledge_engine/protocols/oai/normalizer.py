from __future__ import annotations

from datetime import date

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
        source: str,
    ) -> DocumentMetadata:

        metadata = record.metadata

        def first(name: str) -> str | None:

            values = metadata.get(name)

            if not values:
                return None

            return values[0]

        published_at = None

        if record.datestamp:

            try:
                published_at = date.fromisoformat(
                    record.datestamp[:10]
                )
            except ValueError:
                published_at = None

        authors = metadata.get(
            "creator",
            [],
        )

        identifier = first("identifier")

        if (
            identifier
            and identifier.startswith("http")
        ):
            url = identifier
        else:
            url = "https://example.org"

        return DocumentMetadata(
            title=first("title") or "Sans titre",
            source=source,
            url=url,
            published_at=published_at,
            language=first("language"),
            document_type=first("type"),
            description=first("description"),
            keywords=metadata.get(
                "subject",
                [],
            ),
            author=authors[0] if authors else None,
            authors=authors,
            publisher=first("publisher"),
            identifier=record.identifier,
        )
