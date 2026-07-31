from app.conversation.languages.language_service import (
    LanguageService,
)


class LanguageManager:

    def __init__(self):

        self.service = LanguageService()

    def detect(
        self,
        text: str,
    ) -> str:

        return self.service.detect(
            text
        )
