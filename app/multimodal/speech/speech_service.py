from pathlib import Path

from app.multimodal.models.transcription import (
    Transcription,
)
from app.multimodal.speech.speech_to_text import (
    SpeechToText,
)


class SpeechService:

    def __init__(self):

        self.engine = SpeechToText()

    def transcribe(
        self,
        audio_path: str | Path,
        mime_type: str = "audio/ogg",
    ) -> Transcription:

        return self.engine.transcribe(
            audio_path,
            mime_type=mime_type,
        )