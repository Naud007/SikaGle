from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl

from app.schemas.attachment import DocumentAttachment


class DocumentMetadata(BaseModel):
    """
    Modèle standardisé représentant un document provenant
    d'une source de connaissance.

    Ce modèle est commun à tous les connecteurs
    (BRAB, AGRIS, HAL, Zenodo, OpenAlex, etc.).
    """

    # =========================================================
    # IDENTIFIANT LOCAL (SQLite)
    # =========================================================

    id: Optional[int] = None

    # =========================================================
    # IDENTIFICATION DU DOCUMENT
    # =========================================================

    title: str

    source: str

    url: HttpUrl

    identifier: Optional[str] = None

    # =========================================================
    # INFORMATIONS GÉNÉRALES
    # =========================================================

    published_at: Optional[date] = None

    language: Optional[str] = None

    document_type: Optional[str] = None

    publisher: Optional[str] = None

    # =========================================================
    # CONTENU
    # =========================================================

    content: Optional[str] = None

    description: Optional[str] = None

    # =========================================================
    # MÉTADONNÉES AGRICOLES
    # =========================================================

    crop: Optional[str] = None

    culture: Optional[str] = None

    keywords: list[str] = Field(default_factory=list)

    mots_cles: list[str] = Field(default_factory=list)

    # =========================================================
    # LOCALISATION GÉOGRAPHIQUE
    # =========================================================

    country: Optional[str] = None

    zone_geographique: Optional[str] = None

    # =========================================================
    # AUTEURS
    # =========================================================

    author: Optional[str] = None

    authors: list[str] = Field(default_factory=list)

    # =========================================================
    # INFORMATIONS SUR LE DATASET SOURCE
    # =========================================================

    dataset_filename: Optional[str] = None

    # =========================================================
    # FICHIERS ASSOCIÉS
    # =========================================================

    attachments: list[DocumentAttachment] = Field(
        default_factory=list
    )
