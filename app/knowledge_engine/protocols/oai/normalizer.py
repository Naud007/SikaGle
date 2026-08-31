from __future__ import annotations

from datetime import date

from app.knowledge_engine.protocols.oai.record import OAIRecord
from app.knowledge_engine.resolvers import OJSPDFResolver
from app.schemas.attachment import DocumentAttachment
from app.schemas.document import DocumentMetadata


class OAINormalizer:
    """
    Transforme un OAIRecord en DocumentMetadata.
    """

    def __init__(self):

        self.resolver = OJSPDFResolver()

    def normalize(
        self,
        record: OAIRecord,
        source: str,
    ) -> DocumentMetadata:

        metadata = record.metadata
        
        print(
            "OAI IDENTIFIERS =",
            record.raw_identifiers,
        )

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
        #
        # NOTE (correctif, 31/08/2026) : recherche d'abord un
        # identifiant spécifique à un article (ex: plateforme
        # OJS de BRAB), sinon retombe sur le premier identifiant
        # qui ressemble à une vraie URL http(s) exploitable
        # (par exemple un DOI, https://doi.org/...), plutôt que
        # de toujours utiliser le repli générique example.org.
        # ==================================================

        article_url = "https://example.org"

        fallback_url = None

        for identifier in record.raw_identifiers:

            identifier = identifier.strip()

            if not identifier.startswith("http"):
                continue

            if "/article/view/" in identifier:

                article_url = identifier
                break

            if fallback_url is None:

                fallback_url = identifier

        else:

            if fallback_url:

                article_url = fallback_url

        # ==================================================
        # PIÈCES JOINTES
        # ==================================================

        attachments: list[DocumentAttachment] = []

        if (
            source.upper() == "BRAB"
            and "/article/view/" in article_url
        ):

            pdf_url = self.resolver.resolve(
                article_url
            )

            if pdf_url:

                article_id = (
                    article_url
                    .rstrip("/")
                    .split("/")[-1]
                )

                attachments.append(
                    DocumentAttachment(
                        url=pdf_url,
                        filename=f"{article_id}.pdf",
                        mime_type="application/pdf",
                        file_type="pdf",
                        description="Article scientifique",
                    )
                )

        # ==================================================
        # DOCUMENT NORMALISÉ
        # ==================================================

        return DocumentMetadata(

            title=first("title") or "Sans titre",

            source=source,

            url=article_url,

            published_at=published_at,

            language=first("language"),

            document_type=first("type"),

            description=first("description"),

            keywords=keywords,

            author=authors[0] if authors else None,

            authors=authors,

            publisher=first("publisher"),

            identifier=record.identifier,

            attachments=attachments,
        )
