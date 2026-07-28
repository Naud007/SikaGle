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

            return values[0].strip()

        # ==================================================
        # DATE DE PUBLICATION
        # ==================================================

        published_at = None

        publication_date = first("date")

        if publication_date:

            try:

                published_at = date.fromisoformat(
                    publication_date[:10]
                )

            except ValueError:
                pass

        elif record.datestamp:

            try:

                published_at = date.fromisoformat(
                    record.datestamp[:10]
                )

            except ValueError:
                pass

        # ==================================================
        # AUTEURS (SUPPRESSION DES DOUBLONS)
        # ==================================================

        authors = []

        for author in metadata.get(
            "creator",
            [],
        ):

            author = author.strip()

            if (
                author
                and author not in authors
            ):

                authors.append(author)

        # ==================================================
        # MOTS-CLÉS (SUPPRESSION DES DOUBLONS)
        # ==================================================

        keywords = []

        for keyword in metadata.get(
            "subject",
            [],
        ):

            keyword = keyword.strip()

            if (
                keyword
                and keyword not in keywords
            ):

                keywords.append(keyword)

        # ==================================================
        # URL
        # ==================================================

        identifier = first("identifier")

        if (
            identifier
            and identifier.startswith("http")
        ):

            url = identifier

        else:

            url = "https://example.org"

        # ==================================================
        # DOCUMENT NORMALISÉ
        # ==================================================

        return DocumentMetadata(

            title=first("title") or "Sans titre",

            source=source,

            url=url,

            published_at=published_at,

            language=first("language"),

            document_type=first("type"),

            description=first("description"),

            keywords=keywords,

            author=authors[0] if authors else None,

            authors=authors,

            publisher=first("publisher"),

            identifier=record.identifier,
        )
