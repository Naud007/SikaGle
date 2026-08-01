from app.multimodal.models.output_message import (
    OutputMessage,
)
from app.multimodal.models.speech_response import (
    SpeechResponse,
)


class OutputGenerator:

    def generate(
        self,
        response_text: str,
        modality: str,
        language: str = "fr",
        speech: SpeechResponse | None = None,
    ) -> OutputMessage:

        if modality == "audio":

            return OutputMessage(
                modality="audio",
                audio_path=(
                    speech.audio_path
                    if speech
                    else None
                ),
                language=language,
            )

        return OutputMessage(
            modality="text",
            content=response_text,
            language=language,
        )
