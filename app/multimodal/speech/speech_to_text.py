from pathlib import Path

from app.multimodal.models.transcription import (
    Transcription,
)


class SpeechToText:

    def transcribe(
        self,
        audio_path: str | Path,
    ) -> Transcription:

        audio_path = Path(audio_path)

        if not audio_path.exists():

            raise FileNotFoundError(
                f"Fichier introuvable : {audio_path}"
            )

        #
        # Implémentation V1 :
        # Stub prêt à être remplacé
        # par Whisper/Gemini STT.
        #

        return Transcription(
            text="",
            language="fr",
            confidence=0.0,
        )
