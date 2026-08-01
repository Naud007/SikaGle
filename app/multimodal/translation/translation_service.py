from app.multimodal.models.translation import (
    Translation,
)
from app.multimodal.translation.translator import (
    Translator,
)


class TranslationService:

    def __init__(self):

        self.translator = Translator()

    def translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
    ) -> Translation:

        return self.translator.translate(
            text=text,
            source_language=source_language,
            target_language=target_language,
        )
