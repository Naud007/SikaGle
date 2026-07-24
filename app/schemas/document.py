from datetime import date
from typing import Optional

from pydantic import BaseModel, HttpUrl


class DocumentMetadata(BaseModel):
    """
    Métadonnées standardisées d'un document officiel.
    Tous les connecteurs retourneront ce modèle.
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
