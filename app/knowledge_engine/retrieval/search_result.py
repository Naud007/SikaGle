from dataclasses import dataclass, field


@dataclass
class SearchResult:
    """
    Résultat d'une recherche documentaire.
    """

    document: str

    metadata: dict

    #
    # Scores bruts
    #

    vector_score: float = 0.0

    keyword_score: float = 0.0

    #
    # Score final
    #

    score: float = 0.0

    #
    # Origine
    #

    source: str = "vector"

    #
    # Explications du score
    #

    ranking_details: dict = field(
        default_factory=dict
    )
