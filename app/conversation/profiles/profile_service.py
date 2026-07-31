from app.conversation.models.user_profile import (
    UserProfile,
)
from app.conversation.repositories.profile_repository import (
    ProfileRepository,
)


class ProfileService:

    def __init__(self):

        self.repository = ProfileRepository()

    def get_or_create(
        self,
        user_id: str,
    ) -> UserProfile:

        profile = self.repository.get(
            user_id
        )

        if profile is None:

            profile = UserProfile(
                user_id=user_id,
            )

            self.repository.save(
                profile,
            )

        return profile

    def update(
        self,
        user_id: str,
        **kwargs,
    ) -> UserProfile:

        profile = self.get_or_create(
            user_id,
        )

        for key, value in kwargs.items():

            if hasattr(profile, key):

                setattr(
                    profile,
                    key,
                    value,
                )

        profile.touch()

        self.repository.save(
            profile,
        )

        return profile
