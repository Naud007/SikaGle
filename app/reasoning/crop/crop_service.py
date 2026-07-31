from app.reasoning.crop.crop_detector import (
    CropDetector,
)
from app.reasoning.models.crop import (
    Crop,
)


class CropService:

    def __init__(self):

        self.detector = CropDetector()

    def detect(
        self,
        text: str,
    ) -> Crop:

        return self.detector.detect(
            text
        )
