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

        return ReasoningContext(
            user_id=user_id,
            intent=self.intent_service.detect(
                text
            ),
            crop=self.crop_service.detect(
                text
            ),
            symptoms=self.symptom_service.extract(
                text
            ),
            memory=context.memory,
            history=context.history,
            weather=context.weather,
        )
