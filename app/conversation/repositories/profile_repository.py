from app.conversation.models.user_profile import (
    UserProfile,
)


class ProfileRepository:

    def __init__(self):

        self._profiles: dict[
            str,
            UserProfile,
        ] = {}

    def save(
        self,
        profile: UserProfile,
    ) -> None:

        self._profiles[
            profile.user_id
        ] = profile

    def get(
        self,
        user_id: str,
    ) -> UserProfile | None:

        return self._profiles.get(
            user_id
        )

    def exists(
        self,
        user_id: str,
    ) -> bool:

        return user_id in self._profiles

    def delete(
        self,
        user_id: str,
    ) -> None:

        self._profiles.pop(
            user_id,
            None,
        )
