class LanguageDetector:

    SUPPORTED_LANGUAGES = {
        "fr": "Français",
        "fon": "Fon",
        "yo": "Yoruba",
    }

    def detect(
        self,
        text: str,
    ) -> str:

        text = text.lower()

        if any(
            word in text
            for word in (
                "bonjour",
                "merci",
                "comment",
                "pourquoi",
            )
        ):
            return "fr"

        return "fr"
