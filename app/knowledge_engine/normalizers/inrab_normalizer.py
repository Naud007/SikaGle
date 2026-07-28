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
            description=publication.abstract or "",
            source="inrab",
            language=publication.language or "fr",
            url=publication.detail_url or "",
            download_url=publication.pdf_url,
            keywords=publication.keywords or [],
        )
