from app.multimodal.models.detected_language import (
    DetectedLanguage,
)


class LanguageDetector:

    LANGUAGES = {
        "fr": (
            "Français",
            (
                "bonjour",
                "merci",
                "comment",
                "pourquoi",
            ),
        ),
        "fon": (
            "Fon",
            (),
        ),
        "yo": (
            "Yoruba",
            (),
        ),
    }

    def detect(
        self,
        text: str,
    ) -> DetectedLanguage:

        text = text.lower()

        for code, (
            name,
            keywords,
        ) in self.LANGUAGES.items():

            if any(
                keyword in text
                for keyword in keywords
            ):

                return DetectedLanguage(
                    code=code,
                    name=name,
                    confidence=0.90,
                )

        return DetectedLanguage(
            code="fr",
            name="Français",
            confidence=0.50,
        )
