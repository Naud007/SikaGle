from app.conversation.models.user_profile import (
    UserProfile,
)
from app.conversation.profiles.profile_service import (
    ProfileService,
)


class ProfileManager:

    def __init__(self):

        self.service = ProfileService()

    def get(
        self,
        user_id: str,
    ) -> UserProfile:

        return self.service.get_or_create(
            user_id,
        )

    def update(
        self,
        user_id: str,
        **kwargs,
    ) -> UserProfile:

        return self.service.update(
            user_id,
            **kwargs,
        )
