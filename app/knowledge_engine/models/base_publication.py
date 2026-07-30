from dataclasses import asdict, dataclass
from typing import Optional


@dataclass
class BasePublication:
    """
    Modèle métier de base représentant une publication
    scientifique découverte par un connecteur.
    """

    # ==========================================
    # IDENTITÉ
    # ==========================================

    id: str

    source: str

    # ==========================================
    # MÉTADONNÉES
    # ==========================================

    title: str

    authors: Optional[str] = None

    abstract: Optional[str] = None

    publication_year: Optional[int] = None

    publication_type: Optional[str] = None

    language: Optional[str] = None

    # ==========================================
    # LIENS
    # ==========================================

    pdf_url: Optional[str] = None

    detail_url: Optional[str] = None

    # ==========================================
    # UTILITAIRES
    # ==========================================

    def filename(self) -> str:
        """
        Nom du fichier PDF sur le disque.
        """

        return f"{self.id}.pdf"

    def to_dict(self) -> dict:
        """
        Convertit la publication en dictionnaire.
        """

        return asdict(self)
