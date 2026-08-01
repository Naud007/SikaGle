from app.multimodal.models.detected_language import (
    DetectedLanguage,
)
from app.multimodal.translation.language_detector import (
    LanguageDetector,
)


class LanguageService:

    def __init__(self):

        self.detector = LanguageDetector()

    def detect(
        self,
        text: str,
    ) -> DetectedLanguage:

        return self.detector.detect(
            text
        )
