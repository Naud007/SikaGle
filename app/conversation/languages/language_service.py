from app.conversation.languages.language_detector import (
    LanguageDetector,
)


class LanguageService:

    def __init__(self):

        self.detector = LanguageDetector()

    def detect(
        self,
        text: str,
    ) -> str:

        return self.detector.detect(
            text
        )
