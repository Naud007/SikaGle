class VoiceSelector:

    #
    # NOTE (correctif) :
    #
    # "fr-FR-Standard-A" était un nom de voix au format
    # Google Cloud TTS, incompatible avec Gemini TTS qui
    # utilise des noms de voix simples (ex: "Kore", "Puck").
    # Corrigé uniquement pour le français, qu'on implémente
    # maintenant. Les entrées Fon/Yoruba restent des
    # placeholders à corriger quand ces langues seront
    # traitées (voir feuille de route).
    #

    DEFAULT_VOICES = {
        "fr": "Kore",
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