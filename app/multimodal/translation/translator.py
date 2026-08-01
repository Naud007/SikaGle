from app.multimodal.models.translation import (
    Translation,
)


class Translator:

    PIVOT_LANGUAGE = "fr"

    def translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
    ) -> Translation:

        #
        # Implémentation V1 :
        # Stub prêt à être remplacé
        # par Gemini Translation ou Google Cloud Translation.
        #

        translated_text = text

        return Translation(
            source_language=source_language,
            target_language=target_language,
            original_text=text,
            translated_text=translated_text,
            confidence=1.0,
        )
