from dataclasses import dataclass
from typing import Optional


@dataclass
class INRABPublication:
    """
    Représente une publication découverte sur le portail INRAB.

    Ce modèle correspond aux données brutes extraites du portail,
    avant leur transformation en DocumentMetadata.
    """

    title: str

    authors: Optional[str] = None

    abstract: Optional[str] = None

    publication_year: Optional[int] = None

    publication_type: Optional[str] = None

    domain: Optional[str] = None

    keywords: Optional[list[str]] = None

    pdf_url: Optional[str] = None

    detail_url: Optional[str] = None

    language: Optional[str] = None
