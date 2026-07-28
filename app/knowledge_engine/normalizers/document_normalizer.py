from abc import ABC, abstractmethod

from app.schemas.document import DocumentMetadata


class BaseDocumentNormalizer(ABC):
    """
    Classe de base de tous les normalizers.

    Un normalizer transforme un document brut
    provenant d'un parser en DocumentMetadata.
    """

    @abstractmethod
    def normalize(
        self,
        raw_document
    ) -> DocumentMetadata:
        """
        Transforme un document brut en DocumentMetadata.
        """
        raise NotImplementedError
