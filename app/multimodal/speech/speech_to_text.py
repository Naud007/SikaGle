from pathlib import Path

from google import genai
from google.genai import types

from app.multimodal.models.transcription import (
    Transcription,
)


class SpeechToText:

    def __init__(self):

        self.client = genai.Client()

        self.model = "gemini-3.6-flash"

    def transcribe(
        self,
        audio_path: str | Path,
        mime_type: str = "audio/ogg",
    ) -> Transcription:

        audio_path = Path(audio_path)

        if not audio_path.exists():

            raise FileNotFoundError(
                f"Fichier introuvable : {audio_path}"
            )

        uploaded_file = self.client.files.upload(
            file=str(audio_path),
            config=types.UploadFileConfig(
                mime_type=mime_type
            ),
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=[
                uploaded_file,
                """
Transcris exactement le message audio, PUIS traduis-le en
français si nécessaire.

Réponds STRICTEMENT dans ce format, sur deux lignes,
sans rien ajouter d'autre :

LANGUE: <fr, yo, fon, ou dendi>
TEXTE: <le texte en français>

Si le message est déjà en français, la ligne TEXTE contient
simplement la transcription telle quelle.

Si le message est en Yoruba, en Fon, ou en Dendi, la ligne
TEXTE contient une traduction fidèle et naturelle en français
du sens du message (pas une transcription phonétique).

Ne traduis JAMAIS un nom propre, un nom de lieu, ou un nom de
culture agricole de façon approximative : si tu n'es pas sûr
d'un mot précis, garde-le tel quel plutôt que d'inventer une
traduction.
""",
            ],
        )

        raw_text = (
            response.text
            if response.text
            else ""
        ).strip()

        if not raw_text:

            raise ValueError(
                "Gemini n'a retourné aucune transcription."
            )

        language, translated_text = (
            self._parse_response(
                raw_text
            )
        )

        return Transcription(
            text=translated_text,
            language=language,
            confidence=1.0,
        )

    def _parse_response(
        self,
        raw_text: str,
    ) -> tuple[str, str]:
        """
        Extrait la langue et le texte français depuis la
        réponse structurée de Gemini. En cas de format
        inattendu (Gemini n'a pas respecté le format demandé),
        on retombe sur le français par défaut avec le texte
        brut, plutôt que de faire planter la transcription.
        """

        language = "fr"

        text = raw_text

        for line in raw_text.splitlines():

            stripped = line.strip()

            if stripped.upper().startswith(
                "LANGUE:"
            ):

                language = (
                    stripped
                    .split(
                        ":",
                        1,
                    )[1]
                    .strip()
                    .lower()
                )

            elif stripped.upper().startswith(
                "TEXTE:"
            ):

                text = (
                    stripped
                    .split(
                        ":",
                        1,
                    )[1]
                    .strip()
                )

        if language not in (
            "fr",
            "yo",
            "fon",
            "dendi",
        ):

            language = "fr"

        return language, text