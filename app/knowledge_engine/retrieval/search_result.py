from dataclasses import dataclass, field


@dataclass
class SearchResult:
    """
    Représente un résultat de recherche documentaire.

    Les différents scores sont conservés séparément afin de permettre
    un re-ranking intelligent.
    """

    #
    # Contenu
    #

    document: str

    metadata: dict

    #
    # Scores individuels
    #

    vector_score: float = 0.0

    keyword_score: float = 0.0

    #
    # Score final utilisé pour le classement
    #

    score: float = 0.0

    #
    # Origine du résultat
    #

    source: str = "vector"

    #
    # Informations de classement (debug)
    #

    ranking_details: dict = field(
        default_factory=dict
    )
