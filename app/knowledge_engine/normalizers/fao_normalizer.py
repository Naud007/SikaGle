from app.schemas.document import DocumentMetadata

from app.knowledge_engine.normalizers.document_normalizer import (
    BaseDocumentNormalizer,
)


class FAONormalizer(BaseDocumentNormalizer):
    """
    Normalizer des documents FAO.

    Pour le moment, cette classe sert uniquement
    de fondation.

    Toute la logique actuellement présente dans
    FAODatasetParser sera progressivement déplacée
    ici lors des prochains sprints.
    """

    def normalize(
        self,
        raw_document
    ) -> DocumentMetadata:

        raise NotImplementedError(
            "FAONormalizer non implémenté."
        )
