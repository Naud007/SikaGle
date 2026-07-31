from app.conversation.models.session import Session


class SessionRepository:

    def __init__(self):

        self._sessions: dict[
            str,
            Session,
        ] = {}

    def save(
        self,
        session: Session,
    ) -> None:

        self._sessions[
            session.user_id
        ] = session

    def get(
        self,
        user_id: str,
    ) -> Session | None:

        return self._sessions.get(
            user_id
        )

    def delete(
        self,
        user_id: str,
    ) -> None:

        self._sessions.pop(
            user_id,
            None,
        )

    def exists(
        self,
        user_id: str,
    ) -> bool:

        return user_id in self._sessions

    def all(
        self,
    ) -> list[Session]:

        return list(
            self._sessions.values()
        )
