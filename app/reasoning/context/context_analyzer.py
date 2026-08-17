from app.conversation.context.context_service import (
    ContextService,
)

from app.reasoning.crop.crop_service import (
    CropService,
)

from app.reasoning.models.reasoning_context import (
    ReasoningContext,
)

from app.reasoning.intent.intent_service import (
    IntentService,
)

from app.reasoning.symptoms.symptom_service import (
    SymptomService,
)


class ContextAnalyzer:

    def __init__(self):

        self.context_service = ContextService()

        self.intent_service = IntentService()

        self.crop_service = CropService()

        self.symptom_service = SymptomService()

    def analyze(
        self,
        user_id: str,
        text: str,
    ) -> ReasoningContext:

        context = self.context_service.build(
            user_id
        )

        intent = self.intent_service.detect(
            text
        )

        crop = self.crop_service.detect(
            text
        )

        symptoms = self.symptom_service.extract(
            text
        )

        confidence = self._calculate_confidence(
            intent=intent,
            crop=crop,
            symptoms=symptoms,
        )

        return ReasoningContext(
            user_id=user_id,
            intent=intent,
            crop=crop,
            symptoms=symptoms,
            memory=context.memory,
            history=context.history,
            weather=context.weather,
            confidence=confidence,
        )

    def _calculate_confidence(
        self,
        intent,
        crop,
        symptoms,
    ) -> float:

        values = []

        intent_confidence = getattr(
            intent,
            "confidence",
            None,
        )

        if intent_confidence is not None:
            values.append(
                float(intent_confidence)
            )

        crop_confidence = getattr(
            crop,
            "confidence",
            None,
        )

        if crop_confidence is not None:
            values.append(
                float(crop_confidence)
            )

        for symptom in symptoms:

            symptom_confidence = getattr(
                symptom,
                "confidence",
                None,
            )

            if symptom_confidence is not None:
                values.append(
                    float(symptom_confidence)
                )

        if not values:
            return 0.0

        confidence = sum(values) / len(values)

        return max(
            0.0,
            min(
                1.0,
                confidence,
            ),
        )