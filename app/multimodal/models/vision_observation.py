from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class VisionObservation:
    """
    Résultat structuré de l'analyse d'une photo envoyée par
    un agriculteur, produit par ImageAnalysisService.

    Ce n'est PAS un diagnostic final : c'est une observation
    brute qui sera ensuite transformée en question pour le
    RAG existant (recherche vectorielle + keyword + Gemini),
    qui reste seul responsable de toute recommandation.
    """

    # La photo est-elle exploitable pour une observation
    # utile (nette, bien cadrée, bonne lumière) ?
    photo_usable: bool

    # Si photo_usable est False, message à renvoyer tel quel
    # à l'agriculteur pour lui demander une meilleure photo.
    clarification_needed: str | None = None

    # Culture identifiée sur la photo (ex: "piment"), ou None
    # si non identifiable avec confiance.
    crop: str | None = None

    # Partie de la plante visible (ex: "feuille", "fruit",
    # "tige"), ou None.
    plant_part: str | None = None

    # Description des symptômes visibles, en langage simple
    # (ex: "taches brunes sur les feuilles, feuilles enroulées").
    symptoms: list[str] = field(
        default_factory=list
    )

    # Ravageur ou maladie possible suggéré par l'observation
    # visuelle SEULE (ex: "pucerons") — reste une hypothèse à
    # confirmer par le RAG, jamais un diagnostic final.
    possible_cause: str | None = None

    # Niveau de confiance de l'observation elle-même
    # ("faible", "moyen", "élevé") — PAS un niveau de
    # confiance sur le diagnostic final.
    confidence: str = "faible"

    # Légende éventuelle écrite par l'agriculteur avec sa
    # photo (ex: "mes plants ont des taches").
    caption: str | None = None

    def to_query_text(self) -> str:
        """
        Transforme cette observation en une question textuelle
        exploitable par le pipeline RAG existant (RAGService /
        KnowledgeService), pour ne jamais dupliquer la logique
        de recherche et de sécurité déjà en place.

        IMPORTANT : reste volontairement dense en mots-clés,
        proche de ce qu'un agriculteur taperait naturellement,
        SANS étiquettes ("Culture :", "Symptômes observés :",
        etc.) ni mots de liaison. Ces mots de liaison se
        retrouvaient sinon dans la recherche par mots-clés du
        RAG comme s'il s'agissait de vrais termes agricoles,
        générant une requête trop large qui pouvait expirer
        côté base de données (timeout PostgreSQL observé en
        test réel le 28/08/2026).
        """

        keywords: list[str] = []

        if self.crop:

            keywords.append(
                self.crop
            )

        if self.plant_part:

            keywords.append(
                self.plant_part
            )

        keywords.extend(
            self.symptoms
        )

        if self.possible_cause:

            keywords.append(
                self.possible_cause
            )

        if self.caption:

            keywords.append(
                self.caption
            )

        query = " ".join(keywords)

        return (
            f"{query} : que puis-je faire ?"
        )