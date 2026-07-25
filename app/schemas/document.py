from datetime import date
from typing import Optional

from pydantic import BaseModel, HttpUrl


class DocumentMetadata(BaseModel):
    """
    Modèle standardisé représentant un document
    provenant d'une source de connaissance officielle.

    Ce modèle est volontairement générique afin de permettre
    plus tard l'ajout de :
    - agriculture
    - élevage
    - pêche
    - santé animale
    - météo
    - etc.
    """

    title: str

    source: str

    url: HttpUrl

    published_at: Optional[date] = None

    language: str = "fr"

    country: str = "Bénin"

    crop: Optional[str] = None

    document_type: str = "technical_sheet"

    checksum: Optional[str] = None

    local_path: Optional[str] = None

    # =========================================================
    # CONTENU DU DOCUMENT
    # =========================================================

    content: Optional[str] = None

    # =========================================================
    # MÉTADONNÉES AGRICOLES
    # =========================================================

    description: Optional[str] = None

    culture: Optional[str] = None

    zone_geographique: Optional[str] = None

    mots_cles: Optional[list[str]] = None
