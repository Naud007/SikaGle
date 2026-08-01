from app.multimodal.models.input_message import (
    InputMessage,
)


class InputRouter:

    SUPPORTED_MODALITIES = {
        "text",
        "audio",
    }

    def route(
        self,
        message: InputMessage,
    ) -> str:

        modality = (
            message.modality.lower()
        )

        if (
            modality
            not in self.SUPPORTED_MODALITIES
        ):
            raise ValueError(
                f"Modalité non supportée : {modality}"
            )

        return modality
