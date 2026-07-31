from app.reasoning.intent.intent_detector import (
    IntentDetector,
)
from app.reasoning.models.intent import (
    Intent,
)


class IntentService:

    def __init__(self):

        self.detector = IntentDetector()

    def detect(
        self,
        text: str,
    ) -> Intent:

        return self.detector.detect(
            text
        )
