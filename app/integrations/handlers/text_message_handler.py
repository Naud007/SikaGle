from app.services.agricultural_assistant_service import (
    AgriculturalAssistantService,
)


class TextMessageHandler:
    """
    Traite les messages texte entrants.
    """

    def __init__(self):

        self.assistant = (
            AgriculturalAssistantService()
        )

    def handle(
        self,
        user_id: str,
        message: str,
    ) -> str:

        return self.assistant.process(

            user_id=user_id,

            message=message,

        )