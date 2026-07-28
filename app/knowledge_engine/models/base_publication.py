from dataclasses import dataclass
from typing import Optional


@dataclass
class BasePublication:
    """
    Modèle générique représentant une publication découverte
    par un connecteur du Knowledge Engine.
    """

    title: str

    authors: Optional[str] = None

    abstract: Optional[str] = None

    publication_year: Optional[int] = None

    publication_type: Optional[str] = None

    language: Optional[str] = None

    pdf_url: Optional[str] = None

    detail_url: Optional[str] = None
