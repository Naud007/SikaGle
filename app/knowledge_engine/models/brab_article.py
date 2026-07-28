from dataclasses import dataclass
from typing import Optional

from .base_publication import BasePublication


@dataclass
class BRABArticle(BasePublication):
    """
    Représente un article scientifique publié
    dans le Bulletin de la Recherche Agronomique
    du Bénin (BRAB).
    """

    volume: Optional[str] = None

    issue: Optional[str] = None

    pages: Optional[str] = None

    doi: Optional[str] = None

    journal: str = (
        "Bulletin de la Recherche Agronomique du Bénin"
    )
