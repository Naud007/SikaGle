from dataclasses import dataclass


@dataclass
class SearchQuery:
    """
    Représente une requête de recherche documentaire.
    """

    question: str

    top_k: int = 5

    #
    # Filtres
    #

    source: str | None = None

    language: str | None = None

    publication_type: str | None = None

    publication_year: int | None = None
