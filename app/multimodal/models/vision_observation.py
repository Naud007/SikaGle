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
        Transforme cette observation en une phrase naturelle,
        comme la formulerait l'agriculteur lui-même, exploitable
        par le pipeline RAG existant (RAGService / KnowledgeService).

        Reste dense en mots-clés utiles pour la recherche, tout
        en formulant les informations déjà connues (partie de la
        plante, symptômes) comme des affirmations claires plutôt
        que des mots isolés, pour éviter que Gemini ne redemande
        une information déjà fournie par la photo (bug observé en
        test réel le 28/08/2026 : SikaGlé redemandait "à quel
        endroit ?" alors que la partie de la plante était déjà
        connue).
        """

        crop_phrase = (
            self.crop
            if self.crop
            else "une plante (je n'arrive pas à "
            "identifier la culture sur la photo)"
        )

        sentence = (
            f"J'ai observé {crop_phrase}"
        )

        if self.plant_part:

            sentence += (
                f", sur {self.plant_part}"
            )

        if self.symptoms:

            sentence += (
                " : "
                + ", ".join(self.symptoms)
            )

        sentence += "."

        if self.possible_cause:

            sentence += (
                " Cela pourrait être lié à "
                f"{self.possible_cause}, "
                "mais je n'en suis pas sûr."
            )

        if self.caption:

            sentence += (
                f' L\'agriculteur a ajouté : "{self.caption}"'
            )

        sentence += (
            " Que puis-je faire pour ce problème ?"
        )

        return sentence