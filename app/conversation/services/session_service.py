from app.conversation.models.session import Session
from app.conversation.repositories.session_repository import (
    SessionRepository,
)


class SessionService:

    def __init__(self):

        self.repository = SessionRepository()

    def get_or_create(
        self,
        user_id: str,
    ) -> Session:

        session = self.repository.get(
            user_id
        )

        if session is None:

            session = Session(
                user_id=user_id,
            )

            self.repository.save(
                session
            )

            return session

        if session.expired:

            session = Session(
                user_id=user_id,
            )

            self.repository.save(
                session
            )

            return session

        session.touch()

        self.repository.save(
            session
        )

        return session

    def close(
        self,
        user_id: str,
    ) -> None:

        session = self.repository.get(
            user_id
        )

        if session is None:
            return

        session.expire()

        self.repository.save(
            session
        )
