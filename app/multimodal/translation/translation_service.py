from google import genai

from app.core.retry import call_with_retry


LANGUAGE_NAMES = {
    "yo": "yoruba",
    "fon": "fon",
    "dendi": "dendi",
}


class TranslationService:
    """
    Traduit un texte français vers une langue locale (Yoruba,
    Fon, Dendi), en vue de sa synthèse vocale.

    Utilise Gemini plutôt qu'un service de traduction dédié,
    pour rester cohérent avec le choix fait pour la
    transcription (SpeechToText) : zéro nouvelle intégration
    tant que la qualité n'est pas jugée insuffisante en
    conditions réelles.
    """

    MODEL = "gemini-3.6-flash"

    def __init__(self):

        self.client = genai.Client()

    def translate_from_french(
        self,
        text: str,
        target_language: str,
    ) -> str:

        language_name = LANGUAGE_NAMES.get(
            target_language,
            target_language,
        )

        prompt = f"""
Traduis ce texte français en {language_name}, de façon
naturelle et fidèle, comme le dirait un locuteur natif à
l'oral (le texte sera ensuite lu à voix haute).

Ne traduis JAMAIS un nom propre, un nom de lieu, ou un nom
scientifique de culture/ravageur de façon approximative : si
tu n'es pas sûr d'un mot précis, garde-le tel quel plutôt que
d'inventer une traduction.

Réponds UNIQUEMENT avec le texte traduit, sans aucun
commentaire ni guillemets.

Texte à traduire :
{text}
"""

        response = call_with_retry(
            self.client.models.generate_content,
            model=self.MODEL,
            contents=prompt,
        )

        translated = (
            response.text
            if response.text
            else ""
        ).strip()

        if not translated:

            raise ValueError(
                "Gemini n'a retourné aucune traduction."
            )

        return translated