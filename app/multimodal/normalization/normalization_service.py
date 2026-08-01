from app.multimodal.models.input_message import (
    InputMessage,
)
from app.multimodal.models.normalized_message import (
    NormalizedMessage,
)
from app.multimodal.normalization.content_normalizer import (
    ContentNormalizer,
)


class NormalizationService:

    def __init__(self):

        self.normalizer = (
            ContentNormalizer()
        )

    def normalize(
        self,
        message: InputMessage,
        detected_language: str,
    ) -> NormalizedMessage:

        return self.normalizer.normalize(
            message=message,
            detected_language=detected_language,
        )
