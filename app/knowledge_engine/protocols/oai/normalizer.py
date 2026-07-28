from __future__ import annotations

from datetime import date

from app.knowledge_engine.protocols.oai.record import OAIRecord
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
        # AUTEURS
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
        # MOTS-CLÉS
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
        # URL DE L'ARTICLE
        # ==================================================

        article_url = "https://example.org"

        for identifier in record.raw_identifiers:

            identifier = identifier.strip()

            if (
                identifier.startswith("http")
                and "/article/view/" in identifier
            ):

                article_url = identifier
                break

        # ==================================================
        # URL DU PDF
        # ==================================================

        pdf_url = None

        if (
            source.upper() == "BRAB"
            and "/article/view/" in article_url
        ):

            pdf_url = article_url.rstrip("/") + "/1"

        # ==================================================
        # DOCUMENT NORMALISÉ
        # ==================================================

        return DocumentMetadata(

            title=first("title") or "Sans titre",

            source=source,

            url=article_url,

            pdf_url=pdf_url,

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
