from pathlib import Path

from google import genai

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
    ) -> Transcription:

        audio_path = Path(audio_path)

        if not audio_path.exists():

            raise FileNotFoundError(
                f"Fichier introuvable : {audio_path}"
            )

        uploaded_file = self.client.files.upload(
            file=str(audio_path)
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=[
                uploaded_file,
                """
Transcris exactement le message audio.

Retourne uniquement la transcription,
sans commentaire.

Identifie également la langue utilisée.

Si le message est en français,
retourne le texte en français.

Si le message est en Fon, Yoruba ou Dendi,
conserve la langue originale.
""",
            ],
        )

        text = (
            response.text
            if response.text
            else ""
        ).strip()

        if not text:

            raise ValueError(
                "Gemini n'a retourné aucune transcription."
            )

        language = "fr"

        return Transcription(
            text=text,
            language=language,
            confidence=1.0,
        )