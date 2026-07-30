from dataclasses import dataclass


@dataclass
class SearchResult:
    """
    Représente un résultat de recherche.
    """

    document: str

    metadata: dict

    score: float = 0.0

    source: str = "vector"
