from datetime import date
from typing import Optional

from pydantic import BaseModel, HttpUrl


class DocumentMetadata(BaseModel):
    """
    Modèle standardisé représentant un document
    provenant d'une source de connaissance.

    Ce modèle est générique afin de permettre
    l'intégration progressive de connaissances liées à :

    - agriculture
    - élevage
    - pêche
    - santé animale
    - météo
    - environnement
    - recherche scientifique
    - etc.
    """

    # =========================================================
    # IDENTIFICATION DU DOCUMENT
    # =========================================================

    title: str

    source: str

    url: HttpUrl


    # =========================================================
    # INFORMATIONS GÉNÉRALES
    # =========================================================

    published_at: Optional[date] = None

    language: Optional[str] = None

    document_type: Optional[str] = None


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

    keywords: Optional[list[str]] = None

    mots_cles: Optional[list[str]] = None


    # =========================================================
    # LOCALISATION GÉOGRAPHIQUE
    # =========================================================

    country: Optional[str] = None

    zone_geographique: Optional[str] = None


    # =========================================================
    # AUTEURS / PUBLICATION
    # =========================================================

    author: Optional[str] = None

    authors: Optional[list[str]] = None

    publisher: Optional[str] = None


    # =========================================================
    # INFORMATIONS SUR LE DATASET SOURCE
    # =========================================================

    dataset_filename: Optional[str] = None

    identifier: Optional[str] = None


    # =========================================================
    # STOCKAGE LOCAL
    # =========================================================

    checksum: Optional[str] = None

    local_path: Optional[str] = None
