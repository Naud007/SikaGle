from pathlib import Path

from google import genai
from google.genai import types
from pydantic import BaseModel

from app.core.retry import call_with_retry
from app.multimodal.models.vision_observation import (
    VisionObservation,
)


class _GeminiVisionSchema(BaseModel):
    """
    Schéma interne uniquement utilisé pour contraindre la
    sortie JSON de Gemini (response_schema). Converti ensuite
    vers VisionObservation, notre type interne propre.

    NOTE : tous les champs sont volontairement obligatoires
    (pas de valeur par défaut), car les valeurs par défaut sur
    un response_schema Pydantic sont peu fiables avec l'API
    Gemini actuelle. Le prompt indique explicitement d'utiliser
    une chaîne vide ou une liste vide quand une information est
    inconnue, plutôt que de compter sur une valeur par défaut.
    """

    photo_usable: bool
    clarification_needed: str
    crop: str
    plant_part: str
    symptoms: list[str]
    possible_cause: str
    confidence: str


class ImageAnalysisService:
    """
    Analyse une photo envoyée par un agriculteur avec Gemini
    Vision, et produit une observation structurée (pas un
    diagnostic final — voir VisionObservation).

    Le diagnostic et les recommandations restent entièrement
    du ressort du pipeline RAG existant (RAGService), qui reste
    seul responsable de la sécurité phytosanitaire et de la
    prudence sur l'incertitude.
    """

    MODEL = "gemini-3.6-flash"

    PROMPT = """
Tu analyses une photo envoyée par un agriculteur africain via WhatsApp,
d'une plante qu'il pense malade ou attaquée par un ravageur.

Réponds en observant SEULEMENT ce que tu vois sur l'image, sans jamais
prétendre poser un diagnostic certain. Une photo seule ne permet jamais
de confirmer une maladie ou un ravageur avec certitude.

Remplis les champs suivants :

- photo_usable : est-ce que cette photo est suffisamment nette, bien
  cadrée et bien éclairée pour permettre une observation utile ? Mets
  false si la photo est floue, trop sombre, trop éloignée, ou ne montre
  pas clairement une partie de plante.
- clarification_needed : si photo_usable est false, explique en une
  phrase simple et chaleureuse, comme si tu parlais à l'agriculteur, ce
  qu'il devrait renvoyer (par exemple une photo plus rapprochée, avec
  plus de lumière, du dessous de la feuille). Si photo_usable est true,
  laisse une chaîne vide "".
- crop : la culture visible sur la photo si tu peux l'identifier avec
  une confiance raisonnable (par exemple "piment", "maïs", "tomate"),
  sinon une chaîne vide "".
- plant_part : la partie de la plante visible sur la photo (par exemple
  "feuille", "fruit", "tige", "plant entier"), sinon une chaîne vide "".
- symptoms : liste des symptômes visuels observés, en mots simples
  qu'un agriculteur utiliserait (par exemple "taches brunes", "feuilles
  enroulées", "présence de petits insectes"). Liste vide [] si rien de
  notable n'est visible.
- possible_cause : SEULEMENT si les symptômes sont vraiment évocateurs,
  suggère une hypothèse de ravageur ou de maladie en termes simples
  (par exemple "pucerons"). Laisse une chaîne vide "" si tu n'as pas
  d'hypothèse raisonnable — ne force jamais une hypothèse.
- confidence : "faible", "moyen" ou "élevé", reflétant ta confiance
  dans CETTE OBSERVATION VISUELLE elle-même (pas dans un diagnostic
  final, qui n'est jamais de ton ressort).

Ne mentionne jamais de produit, pesticide, ni de traitement dans ta
réponse : ton rôle ici est uniquement d'observer l'image.
"""

    def __init__(self):

        self.client = genai.Client()

    def analyze(
        self,
        image_path: str | Path,
        mime_type: str = "image/jpeg",
        caption: str | None = None,
    ) -> VisionObservation:

        image_path = Path(image_path)

        if not image_path.exists():

            raise FileNotFoundError(
                f"Fichier introuvable : {image_path}"
            )

        image_bytes = (
            image_path.read_bytes()
        )

        contents = [
            types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type,
            ),
            self.PROMPT,
        ]

        response = call_with_retry(
            self.client.models.generate_content,
            model=self.MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=_GeminiVisionSchema,
            ),
        )

        parsed: _GeminiVisionSchema | None = (
            response.parsed
        )

        if parsed is None:

            raise ValueError(
                "Gemini n'a retourné aucune "
                "observation exploitable pour "
                "cette image."
            )

        return VisionObservation(
            photo_usable=parsed.photo_usable,
            clarification_needed=(
                parsed.clarification_needed
                or None
            ),
            crop=parsed.crop or None,
            plant_part=parsed.plant_part or None,
            symptoms=parsed.symptoms,
            possible_cause=(
                parsed.possible_cause
                or None
            ),
            confidence=(
                parsed.confidence
                or "faible"
            ),
            caption=caption,
        )