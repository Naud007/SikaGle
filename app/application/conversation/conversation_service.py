from uuid import uuid4


class ConversationService:

    def create(self) -> str:

        #
        # Implémentation V1 :
        # Stub prêt à être connecté
        # au Conversation Engine.
        #

        return str(uuid4())

    def get(
        self,
        conversation_id: str,
    ) -> dict:

        return {
            "conversation_id": conversation_id,
        }

    def list(self) -> list[dict]:

        return []

    def delete(
        self,
        conversation_id: str,
    ) -> bool:

        return True
