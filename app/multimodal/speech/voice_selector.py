class VoiceSelector:

    DEFAULT_VOICES = {
        "fr": "fr-FR-Standard-A",
        "fon": "fon-default",
        "yo": "yo-NG-Standard-A",
    }

    def select(
        self,
        language: str,
    ) -> str:

        return self.DEFAULT_VOICES.get(
            language,
            self.DEFAULT_VOICES["fr"],
        )
