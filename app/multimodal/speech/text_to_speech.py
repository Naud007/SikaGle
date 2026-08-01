from pathlib import Path

from app.multimodal.models.speech_response import (
    SpeechResponse,
)
from app.multimodal.speech.voice_selector import (
    VoiceSelector,
)


class TextToSpeech:

    def __init__(self):

        self.voice_selector = VoiceSelector()

    def synthesize(
        self,
        text: str,
        language: str = "fr",
    ) -> SpeechResponse:

        #
        # Implémentation V1 :
        # Stub prêt à être remplacé
        # par Gemini TTS ou Google Cloud TTS.
        #

        voice = self.voice_selector.select(
            language
        )

        return SpeechResponse(
            audio_path=Path(""),
            language=language,
            voice=voice,
            speed=1.0,
        )
