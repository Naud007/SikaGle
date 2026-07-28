from app.knowledge_engine.models import INRABPublication
from app.schemas.document import DocumentMetadata


class INRABNormalizer:
    """
    Convertit une INRABPublication en DocumentMetadata.
    """

    def normalize(
        self,
        publication: INRABPublication,
    ) -> DocumentMetadata:

        return DocumentMetadata(
            title=publication.title,
            source="inrab",
            url=publication.detail_url,
            language=publication.language,
            description=publication.abstract,
            keywords=publication.keywords,
            author=publication.authors,
            publisher="INRAB",
            document_type=publication.publication_type,
        )
