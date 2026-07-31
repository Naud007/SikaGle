from app.conversation.models.session import Session
from app.conversation.services.session_service import (
    SessionService,
)


class SessionManager:

    def __init__(self):

        self.service = SessionService()

    def open(
        self,
        user_id: str,
    ) -> Session:

        return self.service.get_or_create(
            user_id
        )

    def close(
        self,
        user_id: str,
    ) -> None:

        self.service.close(
            user_id
        )

    def get(
        self,
        user_id: str,
    ) -> Session:

        return self.service.get_or_create(
            user_id
        )
